import fiftyone as fo
import fiftyone.brain as fob
import fiftyone.zoo as foz

name = "aic2023-kf-1"
dataset = fo.load_dataset(name)

if __name__ == "__main__":
    # Ensures that the App processes are safely launched on Windows
    session = fo.launch_app(dataset, desktop=True)
    session.wait()