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
    omlmd push localhost:8080/mmortari/mlartifact:v1 model.joblib --metadata md.json
    ```

## Pull

Fetch everything in a single pull:

=== "Python"

    ```py
    omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b")
    ```

=== "CLI"

    ```sh
    omlmd pull localhost:8080/mmortari/mlartifact:v1 -o tmp/a
    ```

Or fetch only the ML model assets:

=== "Python"

    ```py
    omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b", media_types=["application/x-mlmodel"])
    ```

=== "CLI"

    ```sh
    omlmd pull localhost:8080/mmortari/mlartifact:v1 -o tmp/b --media-types "application/x-mlmodel"
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
    omlmd get config localhost:8080/mmortari/mlartifact:v1
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
    omlmd crawl localhost:8080/mmortari/mlartifact:v1 localhost:8080/mmortari/mlartifact:v2 localhost:8080/mmortari/mlartifact:v3
    ```

### Example query

Demonstrate integration of crawling results with querying (in this case using jQ)

> Of the crawled ML OCI artifacts, which one exhibit the max accuracy?

=== "Python"

    ```py
    import jq
    jq.compile( "max_by(.config.customProperties.accuracy).reference" ).input_text(crawl_result).first()
    ```

=== "CLI"

    ```sh
    omlmd crawl \
        localhost:8080/mmortari/mlartifact:v1 \
        localhost:8080/mmortari/mlartifact:v2 \
        localhost:8080/mmortari/mlartifact:v3 \
        | jq "max_by(.config.customProperties.accuracy).reference"
    ```

## To be continued...
