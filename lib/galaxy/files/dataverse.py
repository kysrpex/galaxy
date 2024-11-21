import datetime
import json
import re
import urllib.request
from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Tuple,
)
from urllib.parse import quote

from typing_extensions import (
    Literal,
    TypedDict,
    Unpack,
)

from galaxy.exceptions import AuthenticationRequired
from galaxy.files import OptionalUserContext
from galaxy.files.sources import (
    AnyRemoteEntry,
    DEFAULT_PAGE_LIMIT,
    DEFAULT_SCHEME,
    Entry,
    EntryData,
    FilesSourceOptions,
    RemoteDirectory,
    RemoteFile,
)
from galaxy.files.sources._rdm import (
    RDMFilesSource,
    RDMFilesSourceProperties,
    RDMRepositoryInteractor,
)
from galaxy.util import (
    DEFAULT_SOCKET_TIMEOUT,
    get_charset_from_http_headers,
    requests,
    stream_to_open_named_file,
)

AccessStatus = Literal["public", "restricted"]

class DataverseRDMFilesSource(RDMFilesSource):
    """A files source for Dataverse turn-key research data management repository."""

    plugin_type = "dataverserdm"
    # TODO supports_pagination = True
    # TODO supports_search = True

    def __init__(self, **kwd: Unpack[RDMFilesSourceProperties]):
        super().__init__(**kwd)
        self._scheme_regex = re.compile(rf"^{self.get_scheme()}?://{self.id}|^{DEFAULT_SCHEME}://{self.id}")

    def get_scheme(self) -> str:
        return "dataverse"
    
    # TODO: Test this method
    def score_url_match(self, url: str):
        if match := self._scheme_regex.match(url):
            return match.span()[1]
        else:
            return 0

    # TODO: Test this method    
    def to_relative_path(self, url: str) -> str:
        legacy_uri_root = f"{DEFAULT_SCHEME}://{self.id}"
        if url.startswith(legacy_uri_root):
            return url[len(legacy_uri_root) :]
        else:
            return super().to_relative_path(url)
        
    def get_repository_interactor(self, repository_url: str) -> RDMRepositoryInteractor:
        return DataverseRepositoryInteractor(repository_url, self)
    
    def _list(
        self,
        path="/",
        recursive=True,
        user_context: OptionalUserContext = None,
        opts: Optional[FilesSourceOptions] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        query: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> Tuple[List[AnyRemoteEntry], int]:
        # TODO: Implement this for Dataverse
        pass

    def _create_entry(
        self,
        entry_data: EntryData,
        user_context: OptionalUserContext = None,
        opts: Optional[FilesSourceOptions] = None,
    ) -> Entry:
        # TODO: Implement this for Dataverse
        pass

    # TODO: Test this method
    def _realize_to(
        self,
        source_path: str,
        native_path: str,
        user_context: OptionalUserContext = None,
        opts: Optional[FilesSourceOptions] = None,
    ):
        # TODO: user_context is always None here when called from a data fetch.
        # This prevents downloading files that require authentication even if the user provided a token.

        record_id, filename = self.parse_path(source_path)
        self.repository.download_file_from_record(record_id, filename, native_path, user_context=user_context)

    # TODO: Test this method
    def _write_from(
        self,
        target_path: str,
        native_path: str,
        user_context: OptionalUserContext = None,
        opts: Optional[FilesSourceOptions] = None,
    ):
        record_id, filename = self.parse_path(target_path)
        self.repository.upload_file_to_draft_record(record_id, filename, native_path, user_context=user_context)
    
class DataverseRepositoryInteractor(RDMRepositoryInteractor):
    # TODO: Implement this property for Dataverse?
    # @property
    # def records_url(self) -> str:
    #     return f"{self.repository_url}/api/records"
    
    # TODO: Implement this property for Dataverse?
    # @property
    # def user_records_url(self) -> str:
    #     return f"{self.repository_url}/api/user/records"

    # TODO: Test this method
    def to_plugin_uri(self, record_id: str, filename: Optional[str] = None) -> str:
        return f"{self.plugin.get_uri_root()}/{record_id}{f'/{filename}' if filename else ''}"

    def get_records(
        self,
        writeable: bool,
        user_context: OptionalUserContext = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        query: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> Tuple[List[RemoteDirectory], int]:
        # TODO: Implement this for Dataverse
        pass

    def _to_size_page(self, limit: Optional[int], offset: Optional[int]) -> Tuple[Optional[int], Optional[int]]:
        # TODO: Implement this for Dataverse
        pass

    def get_files_in_record(
        self, record_id: str, writeable: bool, user_context: OptionalUserContext = None
    ) -> List[RemoteFile]:
        # TODO: Implement this for Dataverse
        pass

    def create_draft_record(
        self, title: str, public_name: Optional[str] = None, user_context: OptionalUserContext = None
    ) -> RemoteDirectory:
        # TODO: Implement this for Dataverse
        pass

    def upload_file_to_draft_record(
        self,
        record_id: str,
        filename: str,
        file_path: str,
        user_context: OptionalUserContext = None,
    ):
        # TODO: Implement this for Dataverse
        pass

    def download_file_from_record(
        self,
        record_id: str,
        filename: str,
        file_path: str,
        user_context: OptionalUserContext = None,
    ):
        # TODO: Implement this for Dataverse
        pass

    def _get_download_file_url(self, record_id: str, filename: str, user_context: OptionalUserContext = None):
        """Get the URL to download a file from a record.

        This method is used to download files from both published and draft records that are accessible by the user.
        """
        # TODO: Implement this for Dataverse
        pass

    # TODO: Test this method
    def _is_api_url(self, url: str) -> bool:
        return "/api/" in url

    # TODO: Test this method
    def _to_draft_url(self, url: str) -> str:
        return url.replace("/files/", "/draft/files/")

    def _can_download_from_api(self, file_details: dict) -> bool:
        # TODO: Have a look at this problem

        # Only files stored locally seems to be fully supported by the API for now
        # More info: https://inveniordm.docs.cern.ch/reference/file_storage/
        return file_details["storage_class"] == "L"

    def _is_draft_record(self, record_id: str, user_context: OptionalUserContext = None):
        # TODO: Implement this for Dataverse
        pass

    def _get_draft_record_url(self, record_id: str):
        # TODO: Implement this for Dataverse
        pass

    def _get_draft_record(self, record_id: str, user_context: OptionalUserContext = None):
        # TODO: Implement this for Dataverse
        pass

    def _get_records_from_response(self, response: dict) -> List[RemoteDirectory]:
        # TODO: Implement this for Dataverse
        pass

    # TODO: Implement this for Dataverse
    # def _get_record_title(self, record: InvenioRecord) -> str:
        # pass

    # TODO: Implement this for Dataverse
    # def _get_record_files_from_response(self, record_id: str, response: dict) -> List[RemoteFile]:    
        # pass

    # TODO: Implement this for Dataverse
    # def _get_creator_from_public_name(self, public_name: Optional[str] = None) -> Creator:  
        # pass

    # TODO: Test this method
    def _get_response(
        self,
        user_context: OptionalUserContext,
        request_url: str,
        params: Optional[Dict[str, Any]] = None,
        auth_required: bool = False,
    ) -> dict:
        headers = self._get_request_headers(user_context, auth_required)
        response = requests.get(request_url, params=params, headers=headers)
        self._ensure_response_has_expected_status_code(response, 200)
        return response.json()

    # TODO: Test this method
    def _get_request_headers(self, user_context: OptionalUserContext, auth_required: bool = False):
        token = self.plugin.get_authorization_token(user_context)
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        if auth_required and token is None:
            self._raise_auth_required()
        return headers

    # TODO: Test this method
    def _ensure_response_has_expected_status_code(self, response, expected_status_code: int):
        if response.status_code != expected_status_code:
            if response.status_code == 403:
                self._raise_auth_required()
            error_message = self._get_response_error_message(response)
            raise Exception(
                f"Request to {response.url} failed with status code {response.status_code}: {error_message}"
            )

    # TODO: Test this method
    def _raise_auth_required(self):
        raise AuthenticationRequired(
            f"Please provide a personal access token in your user's preferences for '{self.plugin.label}'"
        )

    # TODO: Test this method
    def _get_response_error_message(self, response):
        response_json = response.json()
        error_message = response_json.get("message") if response.status_code == 400 else response.text
        errors = response_json.get("errors", [])
        for error in errors:
            error_message += f"\n{json.dumps(error)}"
        return error_message


__all__ = ("DataverseRDMFilesSource",)