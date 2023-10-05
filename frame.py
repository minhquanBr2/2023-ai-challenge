class VideoFrame:

    def __init__(self, path, video_name, keyframe_idx, frame_idx, image, similarity):
        self.path = path
        self.video_name = video_name
        self.keyframe_idx = keyframe_idx
        self.frame_idx = frame_idx
        self.image = image
        self.similarity = similarity

    