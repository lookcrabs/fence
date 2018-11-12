import flask

from fence.auth import login_required, require_auth_header
from fence.auth import validate_request
from fence.errors import (
    InternalError,
    NotFound,
    NotSupported,
    Unauthorized,
    UnavailableError,
    UserError,
)

from fence.blueprints.data.indexd import (
    BlankIndex,
    IndexedFile,
    get_signed_url_for_file,
)


blueprint = flask.Blueprint("data", __name__)


@blueprint.route("/<path:file_id>", methods=["DELETE"])
@require_auth_header(aud={"data"})
@login_required({"data"})
def delete_data_file(file_id):
    """
    Delete all the locations for a data file which was uploaded to bucket storage from
    indexd.

    If the data file is still at the first stage where it belongs to just the uploader
    (and isn't linked to a project), then the deleting user should match the uploader
    field on the record in indexd. Otherwise, the user must have delete permissions in
    the project.

    Args:
        file_id (str): GUID of file to delete
    """
    indexd_server = (
        flask.current_app.config.get("INDEXD")
        or flask.current_app.config["BASE_URL"] + "/index"
    )
    indexd_server = indexd_server.rstrip("/")
    response = requests.put("{}/index/{}".format(indexd_server, file_id), json={"urls": []})
    if response.status_code != 200:
        raise InternalError("could not remove URLs from indexd record for file: {}".format(file_id))
    IndexedFile(file_id).delete_files()
    return '', 204


@blueprint.route("/upload", methods=["POST"])
@require_auth_header(aud={"data"})
@login_required({"data"})
def upload_data_file():
    """
    Return a presigned URL for use with uploading a data file.

    See the documentation on the entire flow here for more info:

        https://github.com/uc-cdis/cdis-wiki/tree/master/dev/gen3/data_upload

    """
    # make new record in indexd, with just the `uploader` field (and a GUID)
    blank_index = BlankIndex()
    params = flask.request.get_json()
    if not params:
        raise UserError("wrong Content-Type; expected application/json")
    if "filename" not in params:
        raise UserError("missing required argument `filename`")
    response = {
        "guid": blank_index.guid,
        "url": blank_index.make_signed_url(params["filename"]),
    }
    return flask.jsonify(response), 201


@blueprint.route("/upload/<path:file_id>", methods=["GET"])
def upload_file(file_id):
    """
    Get a presigned url to upload a file given by file_id.
    """
    result = get_signed_url_for_file("upload", file_id)
    return flask.jsonify(result)


@blueprint.route("/download/<path:file_id>", methods=["GET"])
def download_file(file_id):
    """
    Get a presigned url to download a file given by file_id.
    """
    result = get_signed_url_for_file("download", file_id)
    if not "redirect" in flask.request.args or not "url" in result:
        return flask.jsonify(result)
    return flask.redirect(result["url"])
