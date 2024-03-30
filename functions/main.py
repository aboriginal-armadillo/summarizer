# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`


from firebase_functions import storage_fn, options, https_fn, scheduler_fn, logger
from firebase_admin import initialize_app, firestore

from on_upload import handle_upload_internal
from scrape_rss import scrape_rss, individual_article_local

initialize_app()
db = firestore.client()

# initialize_app()


@https_fn.on_request()
def individual_article(req: https_fn.Request) -> https_fn.Response:
    logger.log("individual_article called")
    logger.log(req.args)
    arxiv_id = req.args.get('arxiv_id')
    logger.log(f"individual_article({arxiv_id}) via REST API called")
    individual_article_local(arxiv_id, db)
    logger.log(f"individual_article({arxiv_id}) completed")
    return https_fn.Response("Hello world!")

# @scheduler_fn.on_schedule(schedule="every day 00:33", memory=options.MemoryOption.MB_512)
# def scrape_rss_cron(event: scheduler_fn.ScheduledEvent):
#     scrape_rss("https://rss.arxiv.org/rss/cs.ai+cs.cl+cs.cv+cs.lg", db)

@storage_fn.on_object_finalized(timeout_sec=300, memory=options.MemoryOption.MB_512)
def handle_upload(event: storage_fn.CloudEvent[storage_fn.StorageObjectData]):
    # Get the file name and bucket name from the event data
    file_name = event.data.name
    bucket_name = event.data.bucket
    if file_name.endswith(".pdf"):
        handle_upload_internal(bucket_name, file_name, db)
    logger.log("not a pdf, ignoring")
    # Return a response (optional)
    return 'File upload handled successfully'
