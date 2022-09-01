import os

user = 'test1'
root1 = 'static\pose_capture'
for _, _, filenames in os.walk(root1):
    for filename in filenames:
        if user in filename:
            path = os.path.join(root1, filename)
print(path)