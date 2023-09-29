import fiftyone as fo
import fiftyone.brain as fob
import fiftyone.zoo as foz

name = "aic2023-kf-1d"
dataset_dir = "D:/CS/2023 HCM AI CHALLENGE/keyframes/L01_V001"
dataset_type = fo.types.ImageDirectory

dataset = fo.Dataset.from_dir(
    dataset_dir=dataset_dir,
    dataset_type=dataset_type,
    name=name,
)

image_index = fob.compute_similarity(
    dataset,
    model="clip-vit-base32-torch",
    brain_key="qdrant_index",
    backend="qdrant",
)

query = "human"
view = dataset.sort_by_similarity(
    query,
    brain_key="qdrant_index",
    k=10,  # limit to 10 most similar samples
)

# Delete the Qdrant collection
image_index.cleanup()

# Delete run record from FiftyOne
dataset.delete_brain_run("qdrant_index")

if __name__ == "__main__":
    # Ensures that the App processes are safely launched on Windows
    session = fo.launch_app(dataset, desktop=True)
    session.wait()