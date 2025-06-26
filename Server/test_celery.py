from app.tasks import long_running_task

result = long_running_task.apply_async(args=[5, 7])
print("Waiting for result...")
print("Result:", result.get(timeout=10))  # should print 12 after ~5s