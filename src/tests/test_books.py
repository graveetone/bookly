BASE_URL = "/api/v1/books"


def test_get_all_books(test_client, mock_book_service, mock_session):
    test_client.get(f"{BASE_URL}/")

    assert mock_book_service.get_all_books_called_once_with(mock_session)
