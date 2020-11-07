#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import os
import pathlib
import re
import subprocess
import sys
from types import TracebackType
from typing import List, Dict, Optional, Type, Tuple, Any

# ------------------------------------------------------------------------------

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    fmt = logging.Formatter("%(levelname)s\t%(message)s")
    handler.setFormatter(fmt)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)


# ------------------------------------------------------------------------------


@dataclasses.dataclass
class Repo:
    username: str
    password: str
    server: str
    prefix: str

    def token(self) -> str:
        if not (token := os.environ.get(self.password)):
            raise ValueError(f"{self.password} variable required")
        return token


@dataclasses.dataclass
class Image:
    TAG_RE = re.compile(r"([\w\-]+)(?:/([\w\-.]+))?$")
    SOURCE_LABEL = "org.opencontainers.image.source"

    name: str
    tag: str
    dockerfile: pathlib.Path = dataclasses.field(init=False)
    aliases: List[str] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.__base_dir = pathlib.Path(self.name)

        # --------------

        dockerfile = self.__base_dir / "Dockerfile"
        aliases = ["latest"]

        if (meta_file := self.__base_dir / "meta.json").exists():
            with meta_file.open() as f:
                meta = json.load(f)

            for version in meta:
                dfile = self.__base_dir / version["file"]
                if re.match(version["tag"], self.tag) and dfile.exists():
                    dockerfile = dfile
                    aliases = version["aliases"]

        self.dockerfile: pathlib.Path = dockerfile
        self.aliases: Tuple[str, ...] = aliases

    @property
    def tmp_tag(self) -> str:
        return f"tmp-{self.name}:tmp"

    def full_name(self, repo: Repo) -> str:
        return f"{repo.prefix}{self.name}"

    def validate(self) -> None:
        if not self.dockerfile.exists():
            raise ValueError(f"dockerfile not found: {self.dockerfile}")

        if self.SOURCE_LABEL not in self.dockerfile.read_text():
            raise ValueError(f"source repo label is required: {self.SOURCE_LABEL}")

    @classmethod
    def from_ref(cls, ref: str) -> Image:
        if (m := cls.TAG_RE.match(ref)) is None:
            raise ValueError("invalid tag")

        name, tag = m.groups()
        tag = tag or ""

        image = cls(name=name, tag=tag)
        image.validate()

        return image


class Docker:
    def __init__(self, repo: Repo):
        self.repo = repo
        self.__logged_in = False

    def __enter__(self) -> Docker:
        return self

    def login(self) -> Docker:
        r = subprocess.run(
            [
                "docker",
                "login",
                self.repo.server,
                "-u",
                self.repo.username,
                "--password-stdin",
            ],
            input=self.repo.token().encode(),
            timeout=30,
        )
        r.check_returncode()
        self.__logged_in = True
        return self

    @staticmethod
    def has_image(tag: str) -> bool:
        output = subprocess.check_output(["docker", "images", "--format", "{{.Tag}}", tag])
        return bool(output.strip())

    @staticmethod
    def command(*args: str) -> subprocess.CompletedProcess[bytes]:
        return Docker._command(args, {})

    @staticmethod
    def command_output(*args: str) -> str:
        p = Docker._command(args, {"stdout": subprocess.PIPE})
        return p.stdout.decode()

    @staticmethod
    def _command(args: Tuple[str, ...], sp_args: Dict[str, Any]) -> subprocess.CompletedProcess[bytes]:
        exec_args = ["docker", *args]
        logger.debug("Running: %s", exec_args)
        p = subprocess.run(exec_args, **sp_args)
        p.check_returncode()
        return p

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> None:
        if self.__logged_in:
            self.command("logout", self.repo.server)


# ------------------------------------------------------------------------------


REPOS = [
    Repo(
        username="mkuznets",
        password="GHCR_TOKEN",
        server="ghcr.io",
        prefix="ghcr.io/mkuznets/",
    ),
]

CACHE_REPO = REPOS[0]


def main(ref: str, push: bool, force: bool) -> None:
    image = Image.from_ref(ref)
    tags = {image.tag, *image.aliases}

    cache_tag = None
    if image.aliases:
        cache_tag = f"{image.full_name(CACHE_REPO)}:{image.aliases[0]}"

    if cache_tag and not Docker.has_image(cache_tag):
        # Prefetch the latest image for build cache
        try:
            Docker.command("pull", cache_tag)
        except subprocess.CalledProcessError:
            pass

    cache_args: List[str] = []
    if cache_tag and Docker.has_image(cache_tag):
        cache_args.extend(("--cache-from", cache_tag))

    Docker.command(
        "build",
        image.name,
        "-f",
        str(image.dockerfile),
        "-t",
        image.tmp_tag,
        *cache_args,
    )

    if (version_script := (image.dockerfile.parent / "version.sh")).exists():
        actual_tag = Docker.command_output(
            "run",
            "--rm",
            "-v",
            f"{version_script.absolute()}:/version.sh",
            "--entrypoint=",
            image.tmp_tag,
            "sh",
            "/version.sh",
        ).strip()
        logger.info("Image tag: %s", actual_tag)

        if push and not force and actual_tag != image.tag:
            raise ValueError(f"tag mismatch: `{image.tag}` used, should be `{actual_tag}`")

        tags.add(actual_tag)

    for repo in REPOS:
        release_tags = [f"{image.full_name(repo)}:{t}" for t in filter(None, tags)]

        for tag in release_tags:
            Docker.command("tag", image.tmp_tag, tag)

        if push:
            with Docker(repo).login() as docker:
                for tag in release_tags:
                    docker.command("push", tag)
        else:
            # Local/testing mode: build images once and exit
            break

    Docker.command("rmi", image.tmp_tag)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", help="git tag in the format <image-name>/<version>")
    parser.add_argument("--push", action="store_true", help="push built images to repositories")
    parser.add_argument("--force", action="store_true", help="do not check image tag before push")

    args_ = parser.parse_args()
    main(args_.ref, args_.push, args_.force)
