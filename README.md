<!--
1. migrating from https://github.com/tarilabs/oml
2. remember not to use relative IMGs in this, as it's also being used for pypi
-->

![](https://github.com/tarilabs/omlmd/raw/main/docs/imgs/banner.png)

# OCI Artifact for ML model & metadata

This project is a collection of blueprints, patterns and toolchain (in the form of python SDK and CLI) to leverage OCI Artifact and containers for ML model and metadata.

## Installation

In your Python environment, use:

```
pip install omlmd
```

_Note: CLI coming soon._

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
omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b", media_types=["application/x-artifact"])
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

Demonstrate integration of crawling results with querying (in this case using jQ)

> Of the crawled ML OCI artifacts, which one exhibit the max accuracy?

```py
import jq
jq.compile( "max_by(.config.customProperties.accuracy).reference" ).input_text(crawl_result).first()
```

## To be continued...
