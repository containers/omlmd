<!--
NOTE: headers should align to /README.md
-->

![](https://github.com/containers/omlmd/raw/main/docs/imgs/banner.png)

# OCI Artifact for ML model & metadata

[![Python](https://img.shields.io/badge/python%20-3.9%7C3.10%7C3.11%7C3.12-blue)](https://github.com/containers/omlmd)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Build](https://github.com/containers/omlmd/actions/workflows/build.yaml/badge.svg)](https://github.com/containers/omlmd/actions/workflows/build.yaml)
[![E2E testing](https://github.com/containers/omlmd/actions/workflows/e2e.yaml/badge.svg)](https://github.com/containers/omlmd/actions/workflows/e2e.yaml)
[![PyPI - Version](https://img.shields.io/pypi/v/omlmd)](https://pypi.org/project/omlmd)

[![Static Badge](https://img.shields.io/badge/Website-green?style=plastic&label=Documentation&labelColor=blue)](https://containers.github.io/omlmd)
[![GitHub Repo stars](https://img.shields.io/github/stars/containers/omlmd?label=GitHub%20Repository)](https://github.com/containers/omlmd)
[![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/UCmvDe7dCEmiT4J0XoM6TREQ?label=YouTube%20Playlist)](https://www.youtube.com/watch?v=W4GwIRPXE8E&list=PLdbdefeRIj9SRbg6Hkr15GeyPH0qpk_ww)

This project is a collection of blueprints, patterns and toolchain (in the form of python SDK and CLI) to leverage OCI Artifact and containers for ML model and metadata.

## Installation

In your Python environment, use:

```
pip install omlmd
```

!!! question "Why do I need a Python environment?"

    This SDK follows the same prerequisites as [InstructLab](https://github.com/instructlab/instructlab?tab=readme-ov-file#-installing-ilab) and is intented to offer Pythonic way to create OCI Artifact for ML model and metadata.
    For general CLI tools for containers, we invite you to checkout [Podman](https://podman.io) and all the [Containers](https://github.com/containers/#%EF%B8%8F-tools) toolings.

## Push

Store ML model file `model.joblib` and its metadata in the OCI repository at `localhost:8080`:

=== "Python"

    ```py
    from omlmd.helpers import Helper

    omlmd = Helper()
    omlmd.push("localhost:8080/matteo/ml-artifact:latest", "model.joblib", name="Model Example", author="John Doe", license="Apache-2.0", accuracy=9.876543210)
    ```

=== "CLI"

    ```sh
    omlmd push localhost:8080/mmortari/mlartifact:v1 model.joblib --metadata md.json --plain-http
    ```

## Pull

Fetch everything in a single pull:

=== "Python"

    ```py
    omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b")
    ```

=== "CLI"

    ```sh
    omlmd pull localhost:8080/mmortari/mlartifact:v1 -o tmp/a --plain-http
    ```

Or fetch only the ML model assets:

=== "Python"

    ```py
    omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b", media_types=["application/x-mlmodel"])
    ```

=== "CLI"

    ```sh
    omlmd pull localhost:8080/mmortari/mlartifact:v1 -o tmp/b --media-types "application/x-mlmodel" --plain-http
    ```

### Custom Pull: just metadata

The features can be composed in order to expose higher lever capabilities, such as retrieving only the metadata informatio.
Implementation intends to follow OCI-Artifact convention

=== "Python"

    ```py
    md = omlmd.get_config(target="localhost:8080/matteo/ml-artifact:latest")
    print(md)
    ```

=== "CLI"

    ```sh
    omlmd get config localhost:8080/mmortari/mlartifact:v1 --plain-http
    ```

## Crawl

Client-side crawling of metadata.

_Note: Server-side analogous coming soon/reference in blueprints._

=== "Python"

    ```py
    crawl_result = omlmd.crawl([
        "localhost:8080/matteo/ml-artifact:v1",
        "localhost:8080/matteo/ml-artifact:v2",
        "localhost:8080/matteo/ml-artifact:v3"
    ])
    ```

=== "CLI"

    ```sh
    omlmd crawl localhost:8080/mmortari/mlartifact:v1 localhost:8080/mmortari/mlartifact:v2 localhost:8080/mmortari/mlartifact:v3 --plain-http
    ```

### Example query

Demonstrate integration of crawling results with querying (in this case using [jQ](https://jqlang.github.io/jq))

> Of the crawled ML OCI artifacts, which one exhibit the max accuracy?

=== "Python"

    ```py
    import jq
    jq.compile( "max_by(.config.customProperties.accuracy).reference" ).input_text(crawl_result).first()
    ```

=== "CLI"

    ```sh
    omlmd crawl --plain-http \
        localhost:8080/mmortari/mlartifact:v1 \
        localhost:8080/mmortari/mlartifact:v2 \
        localhost:8080/mmortari/mlartifact:v3 \
        | jq "max_by(.config.customProperties.accuracy).reference"
    ```

## To be continued...
