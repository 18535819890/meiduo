from celery_tasks.main import app

@app.task(name="b_test")
def b_test():
    print("BBBBBB")