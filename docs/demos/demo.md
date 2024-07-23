---
hide:
  - toc
---

<!-- this file is partially generated from the notebooks -->

# Demo 1: Introduction

<div align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/W4GwIRPXE8E" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

This is a work in progress demonstrator; after showing a very simple ML training, we package the ML model assets and relevant metadata as OCI Artifact.
We push the resulting artifact to a specified OCI repository.
We demonstrate how to pull the artifact using standard clients or a customized client.
We demonstrate how to build on top of the provided features, to provide new capabilities, such as custom Pull or local Crawling of metadata for Querying.



# Model Training
We simulate (poorly!) a ML model training and we persist the resulting model in a joblib file.


```python
import joblib
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

X, y = datasets.load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 1, stratify = y)
svc_linear = SVC(kernel="linear", probability=True)
svc_linear.fit(X_train, y_train)

y_pred = svc_linear.predict(X_test)
accuracy_value = accuracy_score(y_test, y_pred)
print("accuracy:", accuracy_value)
```

    accuracy: 0.9777777777777777



```python
with open("model.joblib", 'wb') as fo:  
   joblib.dump(svc_linear, fo)

%ls -lA model*
```

    -rw-r--r--@ 1 mmortari  staff  3299 Jun 17 10:22 model.joblib


# OCI Artifact
Let's leverage OCI-Artifact and OCI-Dist to warehouse our ML model and its metadata.


```python
from omlmd.helpers import Helper

omlmd = Helper()
omlmd.push("localhost:8080/matteo/ml-artifact:latest", "model.joblib", name="Model Example", author="John Doe", license="Apache-2.0", accuracy=accuracy_value)
```

    Successfully pushed localhost:8080/matteo/ml-artifact:latest


| Zot | Quay |
| --- | --- |
| ![](./imgs/Screenshot%202024-06-07%20at%2018.12.04.png) | ![](./imgs/Screenshot%202024-06-12%20at%2010.02.44.png) |

Demonstrate _pull_ with **vanilla** OCI-compliant clients


```python
from oras.provider import Registry

oras_registry = Registry(insecure=True)
oras_registry.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/a")

%ls -lA tmp/a
```

    total 24
    -rw-r--r--@ 1 mmortari  staff  3299 Jun 17 10:22 model.joblib
    -rw-r--r--@ 1 mmortari  staff   269 Jun 17 10:22 model_metadata.oml.json
    -rw-r--r--@ 1 mmortari  staff   187 Jun 17 10:22 model_metadata.oml.yaml


Demonstrate _custom pull_, filtering to download only ML artifact and nothing else


```python
omlmd.pull(target="localhost:8080/matteo/ml-artifact:latest", outdir="tmp/b", media_types=["application/x-artifact"])

%ls -lA tmp/b
```

    total 8
    -rw-r--r--@ 1 mmortari  staff  3299 Jun 17 10:22 model.joblib


Demonstrate custom fetch of metadata layer (following OCI-Artifact conventions)


```python
print(omlmd.get_config(target="localhost:8080/matteo/ml-artifact:latest"))
```

    {"reference":"localhost:8080/matteo/ml-artifact:latest", "config": {
        "name": "Model Example",
        "description": null,
        "author": "John Doe",
        "customProperties": {
            "license": "Apache-2.0",
            "accuracy": 0.9777777777777777
        },
        "uri": null,
        "model_format_name": null,
        "model_format_version": null
    } }


# Crawl OCI-Artifacts

Demonstrator of client-side crawling.
This is only a demonstrator, working on analogous concept server-side (beyond OCI specification, but integrating with it).


```python
# data prep (simulated): store in OCI 3 tags, with different `accuracy` metadata
omlmd.push("localhost:8080/matteo/ml-artifact:v1", "model.joblib", accuracy=.85, name="Model Example", author="John Doe", license="Apache-2.0")
omlmd.push("localhost:8080/matteo/ml-artifact:v2", "model.joblib", accuracy=.90, name="Model Example", author="John Doe", license="Apache-2.0")
omlmd.push("localhost:8080/matteo/ml-artifact:v3", "model.joblib", accuracy=.95, name="Model Example", author="John Doe", license="Apache-2.0")
```

    Successfully pushed localhost:8080/matteo/ml-artifact:v1
    Successfully pushed localhost:8080/matteo/ml-artifact:v2
    Successfully pushed localhost:8080/matteo/ml-artifact:v3


| Zot | Quay |
| --- | --- |
| ![](./imgs/Screenshot%202024-06-07%20at%2018.12.29.png) | ![](./imgs/Screenshot%202024-06-12%20at%2010.07.10.png) |


```python
crawl_result = omlmd.crawl([
    "localhost:8080/matteo/ml-artifact:v1",
    "localhost:8080/matteo/ml-artifact:v2",
    "localhost:8080/matteo/ml-artifact:v3"
])
```

Demonstrate integration of crawling results with querying (in this case using jQ)

> Of the crawled ML OCI artifacts, which one exhibit the max accuracy?


```python
import jq
jq.compile( "max_by(.config.customProperties.accuracy).reference" ).input_text(crawl_result).first()
```




    'localhost:8080/matteo/ml-artifact:v3'


# from ML model in OCI Artifact → to ModelCar

ModelCar's Dockerfile:

```dockerfile
FROM ghcr.io/oras-project/oras:v1.2.0 as builder

RUN oras pull quay.io/mmortari/ml-iris:v1 
 

FROM busybox

RUN mkdir /models && chmod 775 /models
COPY --from=builder /workspace /models/
```


```python
!podman build --load -t mmortari/ml-iris:v1-modelcar -f Containerfile.modelcar .
# !podman push --tls-verify=false mmortari/ml-iris:v1-modelcar localhost:8080/matteo/ml-iris:v1-modelcar
!podman push mmortari/ml-iris:v1-modelcar quay.io/mmortari/ml-iris:v1-modelcar
```

    [1/2] STEP 1/2: FROM ghcr.io/oras-project/oras:v1.2.0 AS builder
    [1/2] STEP 2/2: RUN oras pull quay.io/mmortari/ml-iris:v1 
    --> Using cache 7feb1e5fb58481657bd017001bd1f8ce7f930041f522c29ffcee44bc346bf99c
    --> 7feb1e5fb584
    [2/2] STEP 1/3: FROM busybox
    [2/2] STEP 2/3: RUN mkdir /models && chmod 775 /models
    --> Using cache 4c41b98df27a711498d7e585a7e6a13cc660dc86dc2a30f45fd4d869e5b65091
    --> 4c41b98df27a
    [2/2] STEP 3/3: COPY --from=builder /workspace /models/
    --> Using cache b6a5b03fd625e3a49fd6bd104d250c6efe1be53f48f23db54a1714513e9eb954
    [2/2] COMMIT mmortari/ml-iris:v1-modelcar
    --> b6a5b03fd625
    Successfully tagged localhost/mmortari/ml-iris:v1-modelcar
    Successfully tagged localhost/matteo/ml-iris:v1-modelcar
    b6a5b03fd625e3a49fd6bd104d250c6efe1be53f48f23db54a1714513e9eb954
    Getting image source signatures
    Copying blob sha256:e5744b46b6c629c1861eb438aca266a1a170a519f080db5885cc4e672cd78d1b
    Copying blob sha256:8e13bc96641a6983e79c9569873afe5800b0efb3993c3302763b9f5bc5fb8739
    Copying blob sha256:a1d8fcd2d8014f56ebfd7710bc9487fe01364b8007acca13d75a0127e7f8247a
    Copying config sha256:b6a5b03fd625e3a49fd6bd104d250c6efe1be53f48f23db54a1714513e9eb954
    Writing manifest to image destination


| local Quay | Quay.io |
| --- | --- |
| ![image.png](./imgs/Screenshot%202024-06-17%20at%2014.05.02.png) | ![](./imgs/Screenshot%202024-06-24%20at%2013.12.25.png) |

# from ModelCar → to BootC image (linux+server+model[/car])

bootc containerfile (snippet):

```Dockerfile
FROM quay.io/centos-bootc/centos-bootc:stream9
# ...

# Add quadlet files to setup system to automatically run AI application on boot
COPY quadlet/sklearn.kube quadlet/sklearn.yaml /usr/share/containers/systemd/

# Prepull the model, model_server & application images to populate the system.
# Comment the pull commands to keep bootc image smaller.
# The quadlet .image file added above pulls following images with service startup
RUN podman pull --root /usr/lib/containers/storage docker.io/kserve/sklearnserver:latest
RUN podman pull --root /usr/lib/containers/storage quay.io/mmortari/ml-iris:v1-modelcar

# ...
```


```python
!podman build --build-arg "SSHPUBKEY=$(cat ~/.ssh/id_rsa.pub)" \
       --security-opt label=disable \
	   --cap-add SYS_ADMIN \
	   -f Containerfile.bootc \
	   -t mmortari/ml-iris:v1-bootc .
!podman push mmortari/ml-iris:v1-bootc quay.io/mmortari/ml-iris:v1-bootc
```

    STEP 1/9: FROM quay.io/centos-bootc/centos-bootc:stream9
    STEP 2/9: ARG SSHPUBKEY
    --> Using cache 523580821612112581608763e3943eb40817089f87b690dac045459c0b14fb99
    --> 523580821612
    STEP 3/9: RUN set -eu; mkdir -p /usr/ssh &&     echo 'AuthorizedKeysFile /usr/ssh/%u.keys .ssh/authorized_keys .ssh/authorized_keys2' >> /etc/ssh/sshd_config.d/30-auth-system.conf &&     echo ${SSHPUBKEY} > /usr/ssh/root.keys && chmod 0600 /usr/ssh/root.keys
    --> Using cache 3359a78489d3e4eca5921449532819c1b234660be8ac46f3752dad6ee8989eff
    --> 3359a78489d3
    STEP 4/9: COPY quadlet/sklearn.kube quadlet/sklearn.yaml /usr/share/containers/systemd/
    --> Using cache 5dbe59af0d46b95e74577ce99172e11917622f847d00e4b231cb3d10a937d74a
    --> 5dbe59af0d46
    STEP 5/9: RUN sed -i -e '/additionalimage.*/a "/usr/lib/containers/storage",'         /etc/containers/storage.conf
    --> Using cache e16046b72ce01887444619469f31aa4d758cb7dc8b07c51dd7848cc452349df9
    --> e16046b72ce0
    STEP 6/9: VOLUME /var/lib/containers
    --> Using cache 8c0ce999a83d0f12b4484c750749d8bf7483ebd43862a14dd833f7c91416297e
    --> 8c0ce999a83d
    STEP 7/9: RUN podman pull --root /usr/lib/containers/storage docker.io/kserve/sklearnserver:latest
    --> Using cache 1102e2d0a0bc9d1295d6d78fa44b44774fd365c3c44dcb719c4bbdf549bd81fb
    --> 1102e2d0a0bc
    STEP 8/9: RUN podman pull --root /usr/lib/containers/storage quay.io/mmortari/ml-iris:v1-modelcar
    --> Using cache 8915d99264260de1e7f8b5e4c438e3cb9d66f6ce79fab5c5a7f47608ea71a654
    --> 8915d9926426
    STEP 9/9: RUN podman system reset --force 2>/dev/null
    --> Using cache f2b145347580340b1257bafbd2d0dc4b78452af539c1aa13e4dc7a01b0181c51
    COMMIT mmortari/ml-iris:v1-bootc
    --> f2b145347580
    Successfully tagged localhost/mmortari/ml-iris:v1-bootc
    Successfully tagged localhost/matteo/ml-bootc:latest
    f2b145347580340b1257bafbd2d0dc4b78452af539c1aa13e4dc7a01b0181c51
    Getting image source signatures
    Copying blob sha256:159348fa9cfbb75c5cb57e9fac24b9f28477412149e901bdadb909bfaeb84dad
    Copying blob sha256:9a1a0862c7696bd2e36bf7aad37f9e59a17de5e9ee17e4e7b9e9decc965476e7
    Copying blob sha256:8f4a35e515241f6ad7d2201a35e5ff05332e9fbcae37df036c075817e9b1804b
    
    ...

    Copying blob sha256:4c718200cc93786f4b77f1e43fb517f87e45ff88544789a3390a55c63ec510ec
    Copying blob sha256:c6d68a01008a8b18cc588c38dda4043cf9b1a6ba672a791bc69c796da386e2ec
    Copying blob sha256:c7af602eb478cda4aa9841fb7049eaa3c55a3ed8b347d5a95956c783fe59d472
    Copying config sha256:f2b145347580340b1257bafbd2d0dc4b78452af539c1aa13e4dc7a01b0181c51
    Writing manifest to image destination


Now the bootc container image is available:

![image](./imgs/Screenshot%202024-06-24%20at%2013.22.15.png)

We could also make a Virtual Machine out of it:

![image](./imgs/Screenshot%202024-06-24%20at%2013.26.50.png)

I could run the Virtual Machine and it would serve my model:

![image](./imgs/Screenshot%202024-06-18%20at%2010.35.31_2.png)

and I could interact with it to make Inference:

![](./imgs/Screenshot%202024-06-19%20at%2011.48.25.png)
