import fiftyone as fo
import fiftyone.brain as fob
import fiftyone.zoo as foz

name = "aic2023-kf-1"
dataset_dir = "D:/CS/2023 HCM AI CHALLENGE/keyframes"
dataset_type = fo.types.ImageDirectory

dataset = fo.Dataset.from_dir(dataset_dir=dataset_dir, dataset_type=dataset_type, name=name)
dataset.persistent = True

image_index = fob.compute_similarity(
    dataset,
    model="clip-vit-base32-torch",
    brain_key="img_sim"
)

dataset.save()  

if __name__ == "__main__":
    # Ensures that the App processes are safely launched on Windows
    session = fo.launch_app(dataset, desktop=True)
    session.wait()