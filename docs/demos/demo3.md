---
hide:
  - toc
---

# Demo 3: Signature and Attestation

<div align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/B3K0z8LMROE" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

<!-- TODO revise this lorem ipsum -->

In this demo, we expand on using OCI Artifacts and underlying infrastructure for storing and distributing machine learning model assets, and their metadata. We focus on Signatures and Attestations, which are crucial for building a _trusted model supply chain_. Ensuring a trusted software supply chain is vital, especially in MLOps, where model Provenance and Lineage are essential to confirm that models put into production are secure and traceable.

We demonstrate how to train a machine learning model in a pipeline that provides both a signature and attestation for the resulting OCI artifact. This means that in the OCI repository, we will have the machine learning model, its metadata, and cryptographic signatures to ensure the integrity of the pipeline. The attestation helps us understand the steps and processes that led to the creation of the OCI artifact, supporting transparency and trust in the model's origin.

Our demo uses Tekton Chains to generate cryptographic signatures and attestations, but the underlying principles apply to any standard technology such as `in-toto` or `SLSA`. We show the training process using a simple Python script that loads data, trains a model, computes accuracy, and then pushes the result to a container repository. This example illustrates the ease of integrating cryptographic signature support into a machine learning pipeline.

We then go through the steps of creating signing keys, setting up authentication for the OCI repository, and running the pipeline. The process includes loading data, training the model, and pushing the artifact to the repository, where it is signed and attested. The signatures and attestations are verified using the public key, ensuring the artifact's integrity and providing detailed information on how it was created.

Finally, we summarize the importance of using well-known infrastructure for producing and verifying machine learning models and their metadata. The demonstrated infrastructure is composable, allowing for parameterization of input and output, and adaptable to various CI/CD providers. By using these foundational building blocks, we can better manage model provenance and lineage, ensuring a secure and trusted machine learning model supply chain.
