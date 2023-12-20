'''
def test_index(client):
    rv = client.get("/")

    assert '新規登録' in rv.data.decode()
    assert "ログイン" in rv.data.decode()
    assert "画像新規登録" in rv.data.decode()'''




def signup(client, username, email, password):
    data = dict(username=username, email=email, password=password)
    return client.post("/auth/signup", data=data, follow_redirects=True)



def test_index_signup(client):
    rv = signup(client, "admin", "scrapy@example.com", "password")
    assert "admin" in rv.data.decode()
    
    rv = client.get("/")
    assert "ログアウト" in rv.data.decode()
    assert "画像新規登録" in rv.data.decode()
    assert "detector" in rv.data.decode()
    
'''
def test_upload_word_no_auth(client):
    rv = client.get("/upload_word", follow_redirects=True)
    
    print(rv.data.decode())
    assert "論文検索" not in rv.data.decode()
    
    assert "メールアドレス" in rv.data.decode()
    assert "パスワード" in rv.data.decode()
'''

def test_upload_word_signup(client):
    signup(client, "admin", "scrapy@example.com", "password")
    rv = client.get("/upload_word")
    assert "検索" in rv.data.decode()
    assert "admin" in rv.data.decode()
    assert "ログアウト" in rv.data.decode()
    assert "論文検索" in rv.data.decode()
    
def test_delete_object(client):
    signup(client, "admin", "scrapy@example.com", "password")
    