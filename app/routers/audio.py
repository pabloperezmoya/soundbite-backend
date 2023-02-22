import datetime
from fastapi import APIRouter, Body, File, Path, UploadFile, BackgroundTasks, status, HTTPException, Request, Form
from services.database import DatabaseService
from services.storage import StorageService

from fastapi.responses import StreamingResponse

import uuid

router = APIRouter(prefix="/audio", tags=["Audio"])

@router.post(
    path="/share/{share_id}/{user_id}",
    status_code=status.HTTP_200_OK,
)
def get_share_document(share_id: str = Path(...), user_id: str = Path(...)):
    """
    # Get share document from database
    
    User who received and share link use this endpoint to get the audio document,
    and append it to his own audio collection.

    Args:
        share_id (str): Share id
        user_id (str): User id
    
    Raises:
        HTTPException: If share document not found
        HTTPException: If user is trying to share his own audio
    """

    if user_id == "undefined":
        raise HTTPException(status_code=400, detail="User not logged in")
    try:
        # Getting document from database
        # contains audio_id and user_id (who created the share)
        res_share = DatabaseService().get_share_document(share_id)
        
        # Checking if share document exists
        if res_share is None:
            raise HTTPException(status_code=404, detail=f"Share document not found, {res_share}")

        if user_id == res_share["user_id"]:
            raise HTTPException(status_code=400, detail="You can't share your own audio")

        # Get audio document from database by the user_id who created the share
        audio_doc = DatabaseService().get_audio_document(res_share["audio_id"])


        unique_id = f"{uuid.uuid4().hex}.mp3"
        res_append = DatabaseService().append_audio_document({
                "_id": unique_id ,
                "user_id": user_id,
                "shared_by": audio_doc['user_id'],
                "file_name": audio_doc['file_name'],
                "name": audio_doc['name'],
                "duration": audio_doc['duration'],
                "stream_url": audio_doc['stream_url'],
                "uploaded_at": datetime.datetime.now()
        })
        if not res_append.acknowledged:
          raise HTTPException(status_code=500, detail="Error uploading audio")
    except Exception:
        return HTTPException(status_code=500, detail="Error getting share document")


@router.post(
    path="/share/create",
    status_code=status.HTTP_201_CREATED,
)
def create_audio_share(audio_id: str = Body(...), user_id: str = Body(...)):
    """
    # Create audio share document in database.

    Here we create a document in the database that contains the audio_id and the user_id, 
    this document will be used to get the audio document from the database and append it to the user collection.

    Args:
        audio_id (str, optional): _description_. Defaults to Body(...).
        user_id (str, optional): _description_. Defaults to Body(...).

    Returns:
        dict: Contains the share_id
    """

    document = {
        "audio_id": audio_id,
        "user_id": user_id,
        "created_at": datetime.datetime.now(),
        "expire_at": datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    }

    try:
        res = DatabaseService().create_share_document(document)
        return {"_id": str(res.inserted_id)}
    except Exception:
        return HTTPException(status_code=500, detail="Error creating share")


@router.get("/all/{user_id}")
async def get_all_audios_from_user(user_id: str):
    """
    # Get all audios from user

    Args:
        user_id (str)

    Returns:
        list: List of audio documents
    """

    # Call to database to get all audios from user
    try:
        res = DatabaseService().get_all_audios_from_user(user_id)
        return list(reversed([ audio for audio in res]))
    except Exception:
        return HTTPException(status_code=500, detail="Error getting audios")
    


@router.get("/{audio_id}")
async def get_audio(audio_id: str):
    """
    # Get audio document from database

    Args:
        audio_id (str)

    Returns:
        dict: contains audio document
    """

    # Call to storage service to get audio document
    try:
        res = DatabaseService().get_audio_document(audio_id)
        return res
    except Exception:
        return HTTPException(status_code=500, detail="Error getting audios")
    


@router.get("/{audio_id}/stream")
async def get_audio_stream(audio_id: str, request: Request) -> StreamingResponse:
    """
    # Get audio stream from storage service

    Get the audio stream from the storage service and return it as a StreamingResponse

    Args:
        audio_id (str):
        request (Request): Required by browser to play audio

    Returns:
        StreamingResponse: Audio stream
    """

    # Call to storage service to get audio as stream
    try:
        ss = StorageService()
        stream = ss.get(audio_id)
        return return_stream(stream)

    except Exception:
        return HTTPException(status_code=500, detail="Error getting audios")

def return_stream(stream) -> StreamingResponse:
    def iterfile():
        yield from stream.iter_content(chunk_size=1024)
    return StreamingResponse(
        iterfile(),
        status_code=200,
        media_type="audio/mpeg",
        headers=stream.headers
        )



@router.post(
    path="/upload/{user_id}",
    status_code=status.HTTP_201_CREATED
)
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...), name: str  = Form(), duration: str  = Form(), user_id: str = Path(...), ):
    """
    # Upload audio to storage service
    In a logic way it should be better to upload the audio to the storage service first and then to the database,
    but in this case we are using a free storage service and it has a limit of 5GB, so we are uploading the audio to the database first and then to the storage service.

    Also, using background_tasks we can run the function async, but in this case we are not using it because we want to check if the audio was uploaded to the database before uploading it to the storage service.

    Args:
        background_tasks (BackgroundTasks): Used to run the function async
        file (UploadFile, optional): . Defaults to File(...).
        name (str, optional): . Defaults to Form().
        duration (str, optional): . Defaults to Form().
        user_id (str, optional): . Defaults to Path(...).


    Returns:
        string: inserted_id
    """
    
    # Check if file is audio
    if not file.content_type.startswith("audio"):
        raise HTTPException(status_code=400, detail="File is not audio")

    unique_id = f"{uuid.uuid4().hex}.mp3"
    # Upload audio to storage service
    try:
        ss = StorageService()
        # background_tasks.add_task(ss.put, unique_id, file.file) . USE THIS IF YOU WANT TO RUN THE FUNCTION ASYNC
        ss.put(unique_id, file.file)
    except Exception:
        raise HTTPException(status_code=500, detail="Error uploading audio")

    # Call to database to save audio document
    res = DatabaseService().append_audio_document({
        "_id": unique_id,
        "user_id": user_id,
        "file_name": file.filename,
        "name": name,
        "duration": duration,
        "stream_url": f"/audio/{unique_id}/stream",
        "uploaded_at": datetime.datetime.now()
    })
    if not res.acknowledged:
        raise HTTPException(status_code=500, detail="Error uploading audio")

    return res.inserted_id

@router.delete(
    path="/delete/{user_id}/{audio_id}",
    status_code=status.HTTP_200_OK
    )
async def delete_audio(background_tasks: BackgroundTasks, user_id:str = Path(...), audio_id: str = Path(...)):
    """
    # Delete audio from storage service
    Using background_tasks we can run the function async.
    User clicks on delete button, the audio is deleted from the storage service (in an async way) and then from the database.

    Args:
        background_tasks (BackgroundTasks): Used to run the function async
        user_id (str, optional): Defaults to Path(...).
        audio_id (str, optional): Defaults to Path(...).

    Returns:
        200 status code
    """

    try:
        ss = StorageService()
        background_tasks.add_task(ss.delete, audio_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Error uploading audio")

    # Call to database to delete audio document
    res = DatabaseService().delete_audio_document(audio_id)
    if not res.acknowledged:
        raise HTTPException(status_code=500, detail="Error uploading audio")

@router.put(
    path="/update/{user_id}/{audio_id}/{name}",
    status_code=status.HTTP_200_OK
)
async def update_audio_name(user_id: str = Path(...), audio_id: str = Path(...), name: str = Path(...)):
    """
    # Update audio name


    Args:
        user_id (str, optional): Defaults to Path(...).
        audio_id (str, optional): Defaults to Path(...).
        name (str, optional): Defaults to Path(...).

    Raises:
        HTTPException: _description_
    """
    
    res = DatabaseService().update_audio_document(audio_id, {"name": name})
    if not res.acknowledged:
        raise HTTPException(status_code=500, detail="Error uploading audio")
