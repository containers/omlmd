<!-- migrating from https://github.com/tarilabs/oml -->

Using OCI Artifact for ML model and metadata

# Installation

```
pip install omlmd
```

# Push

```py
from omlmd.helpers import Helper

omlmd = Helper()
omlmd.push("localhost:8080/matteo/ml-artifact:latest", "model.joblib", name="Model Example", author="John Doe", license="Apache-2.0", accuracy=9.876543210)
```

# Pull

```py
omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b", media_types=["application/x-artifact"])
```

# Custom Pull: only metadata layer

Implementation intends to follow OCI-Artifact convention

```py
md = omlmd.get_config(target="localhost:8080/matteo/ml-artifact:latest")
print(md)
```

# Crawl

Client-side crawling of metadata.

Note: server-side analogous, reference in blueprints.

```py
crawl_result = omlmd.crawl([
    "localhost:8080/matteo/ml-artifact:v1",
    "localhost:8080/matteo/ml-artifact:v2",
    "localhost:8080/matteo/ml-artifact:v3"
])
```

## Example query

Demonstrate integration of crawling results with querying (in this case using jQ)

> Of the crawled ML OCI artifacts, which one exhibit the max accuracy?

```py
import jq
jq.compile( "max_by(.config.customProperties.accuracy).reference" ).input_text(crawl_result).first()
```

# To be continued...
