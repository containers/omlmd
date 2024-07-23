---
hide:
  - toc
---

# Demo 2: more about ModelCar

<div align="center">
<iframe width="560" height="315" src="https://www.youtube.com/embed/n2Fmt-hsnLM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

<!-- TODO revise this lorem ipsum -->

In this follow-up demo, we focus on using OCI Artifacts for Machine Learning model assets and their metadata, specifically within the context of "ModelCar". We start by recapping the previous setup where we wrapped a machine learning model as an OCI artifact and then as a ModelCar. Today, we'll explore three demos: using the ModelCar in a traditional KServe setup, using it within a KServe raw environment, and directly utilizing the OCI artifact in KServe with a custom storage initializer.

First, we demonstrate using the ModelCar in a traditional KServe setup. We begin by interacting with the machine learning model locally to understand the input and output behavior. After preparing a KServe cluster, we deploy the ModelCar and verify it by making predictions using test data. The predictions align with our expectations, demonstrating that the ModelCar works correctly within the KServe environment.

Next, we move to a KServe Raw environment to show the versatility of the ModelCar. We prepare a KServe Raw-enabled cluster and deploy the ModelCar following similar steps as in the traditional setup. We interact with the deployed model in KServe Raw, confirming that it predicts the same class values for given inputs, just as it did in the KServe setup. This consistency underscores the ModelCar's compatibility across different serving environments.

In the final demo, we highlight the power of composition by using the OCI Artifact directly in KServe. We define a custom storage initializer for OCI Artifacts using the provided library. This allows us to deploy the machine learning model directly from the OCI artifact without wrapping it in a ModelCar. We apply the custom storage initializer in our Kubernetes cluster and interact with the model, achieving the same prediction results as before. This demonstrates the flexibility and compositional power of the underlying OCI infrastructure.

Throughout these demos, we illustrate how the ModelCar and OCI artifacts can be seamlessly integrated and utilized within different Kubernetes-based serving environments. The consistent prediction results across local, KServe, and KServe Raw setups validate the robustness of this approach. Additionally, the use of a custom storage initializer showcases the adaptability of the system to handle OCI artifacts directly.

In conclusion, we have demonstrated the workflow from wrapping a machine learning model as an OCI Artifact, deploying it as a ModelCar, and using it in different serving environments. We also showcased the direct use of OCI Artifacts with a custom storage initializer, highlighting the flexibility and scalability offered by KServe and Kubernetes. These demos provide a comprehensive view of how to leverage OCI Artifacts for efficient and scalable machine learning model deployment.
