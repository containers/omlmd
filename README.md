<!--
1. migrating from https://github.com/tarilabs/oml
2. remember not to use relative IMGs in this, as it's also being used for pypi
-->

![](https://github.com/tarilabs/omlmd/raw/main/docs/imgs/banner.png)

# OCI Artifact for ML model & metadata

[![Python](https://img.shields.io/badge/python%20-3.9%7C3.10%7C3.11%7C3.12-blue)](https://github.com/tarilabs/omlmd)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Build](https://github.com/tarilabs/omlmd/actions/workflows/build.yaml/badge.svg)](https://github.com/tarilabs/omlmd/actions/workflows/build.yaml)
[![E2E testing](https://github.com/tarilabs/omlmd/actions/workflows/e2e.yaml/badge.svg)](https://github.com/tarilabs/omlmd/actions/workflows/e2e.yaml)
[![PyPI - Version](https://img.shields.io/pypi/v/omlmd)](https://pypi.org/project/omlmd)

[![Static Badge](https://img.shields.io/badge/Website-green?style=plastic&label=Documentation&labelColor=blue)](https://tarilabs.github.io/omlmd)
[![GitHub Repo stars](https://img.shields.io/github/stars/tarilabs/omlmd?label=GitHub%20Repository)](https://github.com/tarilabs/omlmd)
[![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/UCmvDe7dCEmiT4J0XoM6TREQ?label=YouTube%20Playlist)](https://www.youtube.com/watch?v=W4GwIRPXE8E&list=PLdbdefeRIj9SRbg6Hkr15GeyPH0qpk_ww)

This project is a collection of blueprints, patterns and toolchain (in the form of python SDK and CLI) to leverage OCI Artifact and containers for ML model and metadata.

Documentation: https://tarilabs.github.io/omlmd

GitHub repository: https://github.com/tarilabs/omlmd <br/>
YouTube video playlist: https://www.youtube.com/watch?v=W4GwIRPXE8E&list=PLdbdefeRIj9SRbg6Hkr15GeyPH0qpk_ww <br/>
Pypi distribution: https://pypi.org/project/omlmd <br/>

## Installation

> [!TIP]
> We recommend checking out the [Getting Started tutorial](https://tarilabs.github.io/omlmd) in the documentation; below instructions are provided for a quick overview.

In your Python environment, use:

```
pip install omlmd
```

## Push

Store ML model file `model.joblib` and its metadata in the OCI repository at `localhost:8080`:

```py
from omlmd.helpers import Helper

omlmd = Helper()
omlmd.push("localhost:8080/matteo/ml-artifact:latest", "model.joblib", name="Model Example", author="John Doe", license="Apache-2.0", accuracy=9.876543210)
```

## Pull

Fetch everything in a single pull:

```py
omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b")
```

Or fetch only the ML model assets:

```py
omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b", media_types=["application/x-mlmodel"])
```

### Custom Pull: just metadata

The features can be composed in order to expose higher lever capabilities, such as retrieving only the metadata informatio.
Implementation intends to follow OCI-Artifact convention

```py
md = omlmd.get_config(target="localhost:8080/matteo/ml-artifact:latest")
print(md)
```

## Crawl

Client-side crawling of metadata.

_Note: Server-side analogous coming soon/reference in blueprints._

```py
crawl_result = omlmd.crawl([
    "localhost:8080/matteo/ml-artifact:v1",
    "localhost:8080/matteo/ml-artifact:v2",
    "localhost:8080/matteo/ml-artifact:v3"
])
```

### Example query

Demonstrate integration of crawling results with querying (in this case using [jQ](https://jqlang.github.io/jq))

> Of the crawled ML OCI artifacts, which one exhibit the max accuracy?

```py
import jq
jq.compile( "max_by(.config.customProperties.accuracy).reference" ).input_text(crawl_result).first()
```

## To be continued...

Don't forget to checkout the [documentation website](https://tarilabs.github.io/omlmd) for more information!
