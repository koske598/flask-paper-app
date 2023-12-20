from apps.app import db
from apps.crud.models import User
from flask_app.apps.scrapy.models import UserKeyword
from flask import Blueprint, current_app, render_template, redirect, url_for, flash
from apps.scrapy.forms import SerchWordForm, DeleteForm
from sqlalchemy.exc import SQLAlchemyError
import spacy
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import seaborn as sns
from flask_login import current_user, login_required
import boto3
import requests
from apps import setting
from dotenv import load_dotenv
from os.path import join, dirname


load_dotenv(verbose=True, override=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

sc = Blueprint("scrapy", __name__, template_folder="templates")


@sc.route("/")
def index():
    if current_user.is_authenticated:
    #ログインユーザーが入力したキーワードの一覧取得
        user_keywords = db.session.query(User, UserKeyword).join(UserKeyword).filter(User.id == current_user.id).all()
        

        s3 = boto3.client('s3', aws_access_key_id=setting.AWS_ACCESS_KEY_ID, aws_secret_access_key= setting.AWS_SECRET_ACCESS_KEY)
        bucket_name = 'mytextbukcet'

        url_list = []
        # 各オブジェクトのURLを生成して表示
        for user_keyword in user_keywords:
            keyword = user_keyword.UserKeyword.keyword
            year1 = user_keyword.UserKeyword.year1
            year2 = user_keyword.UserKeyword.year2
            object_url = f'https://{bucket_name}.s3.amazonaws.com/{keyword}_{year1}_{year2}.jpg'
            url_list.append(object_url)
        
        delete_form = DeleteForm()
    
    else:
        flash('ログインが必要です')
        return render_template("auth/index.html")
    return render_template("scrapy/index_book3.html",user_keywords=user_keywords, delete_form=delete_form,url_list=url_list)



@sc.route("/upload_word", methods=["GET", "POST"])
@login_required
def upload_word():
    form = SerchWordForm()
    if form.validate_on_submit():
        keyword = form.keyword.data
        year1 = form.year1.data
        year2 = form.year2.data
        user_keyword = UserKeyword(user_id=current_user.id, keyword = keyword, year1 = year1, year2 = year2) 
        try:
            if int(year1) <= int(year2):
                db.session.add(user_keyword)
                db.session.commit()
                
                return redirect(url_for('scrapy.scrapy'))
        
        except SQLAlchemyError as e:
            flash("検索期間を正しく入力してください。","error")
            db.session.rollback()
            current_app.logger.error(e)
    return render_template("scrapy/search.html", form=form)


def get_paper_abstract(keyword, year1, year2):
    api_key = setting.CORE_API_KEY
    url = f"https://api.core.ac.uk/v3/search/works/?api_key={api_key}" 
    
    query = f"{keyword} AND yearPublished>={year1} AND yearPublished<={year2}"

    # APIを呼び出し、論文タイトルを取得
    params = {
        "apiKey": api_key,
        "q": query,
        "limit": 100,
        "scroll": True
    }

    title_list = []
    abstract_list = []
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        for key in data['results']:
            title_list.append(key['title']) # titleのみ参照
        for key in data['results']:
            abstract_list.append(key['abstract']) # titleのみ参照s
    
    return title_list #, abstract_list


def text_mining(title_list, keyword, year1, year2):
    
    titles = []
    for title in title_list:
        titles.append(title)
    
    titles = ','.join(titles)
    
    nlp = spacy.load("en_core_web_sm")
    
    # テキストを解析
    doc = nlp(titles)

    # 単語を抽出してリストに格納
    words = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]

    # 単語の出現頻度を計算
    word_freq = Counter(words)

    # グラフ化
    top_words = 20  # グラフに表示するトップ単語の数を指定

    # 出現頻度が高い単語を取得
    most_common_words = word_freq.most_common(top_words)
    
    fp = matplotlib.font_manager.FontProperties(fname = r'C:\WINDOWS\Fonts\msgothic.ttc', size=12 )

    # グラフの作成
    plt.figure(figsize=(10, 6))
    sns.barplot(x=[word[1] for word in most_common_words], y=[word[0] for word in most_common_words], palette="viridis")
    plt.xlabel('出現頻度', fontproperties=fp)
    plt.ylabel('単語', fontproperties=fp)
    plt.title(f'検索ワード {keyword} / 検索期間 {year1}-{year2} ', fontproperties=fp)
    plt.xticks(rotation=45)

    # グラフをファイル形式で保存
    plt.savefig(f'{keyword}_{year1}_{year2}.jpg', format='jpg')
    
    
    # AWS S3へのアップロード
    s3 = boto3.client('s3', aws_access_key_id=setting.AWS_ACCESS_KEY_ID, aws_secret_access_key= setting.AWS_SECRET_ACCESS_KEY)
    bucket_name = 'mytextbukcet'
    metadata = {
        'keyword': keyword,
        'year1': year1,
        'year2': year2
    }
    s3.upload_file(f'{keyword}_{year1}_{year2}.jpg', bucket_name, f'{keyword}_{year1}_{year2}.jpg', ExtraArgs={'Metadata': metadata})
    
    # 画像のURLを生成
    s3_url = f'https://{bucket_name}.s3.amazonaws.com/{keyword}_{year1}_{year2}.jpg'
    
    return s3_url



@sc.route("/scrapy/scrapy", methods=['POST','GET'])
@login_required
def scrapy():
    #直近で入力したkeywordレコードを取得
    keyword = (
        db.session.query(UserKeyword).order_by(UserKeyword.created_at.desc()).first()  #一旦除外.filter(UserKeyword.id == keyword_id)
    )
    
    if keyword.keyword is None:
        flash("失敗です")
        return redirect(url_for('scrapy.index'))
    
    title_list = get_paper_abstract(keyword.keyword, keyword.year1, keyword.year2)

    try:
        #save_paper(title_list, keyword)
        s3_url = text_mining(title_list, keyword.keyword, keyword.year1, keyword.year2)
    
    except SQLAlchemyError as e:
        flash("エラー発生")
        
        db.session.rollback()
        
        current_app.logger.error(e)
        return redirect(url_for('scrapy.index'))
    
    return redirect(url_for("scrapy.index"))



@sc.route("/delete/<string:keyword_id>", methods=['POST'])
@login_required
def delete_object(keyword_id):
    
    s3 = boto3.client('s3', aws_access_key_id=setting.AWS_ACCESS_KEY_ID, aws_secret_access_key= setting.AWS_SECRET_ACCESS_KEY)
    bucket_name = 'mytextbukcet'
    
    try:
        user_keyword = (db.session.query(UserKeyword).filter(UserKeyword.id == keyword_id).first())
        # 削除するオブジェクトのURLを作製
        keyword = user_keyword.keyword
        year1 = user_keyword.year1
        year2 = user_keyword.year2
        object_url = f'https://{bucket_name}.s3.amazonaws.com/{keyword}_{year1}_{year2}.jpg'
        s3.delete_object(Bucket=bucket_name, Key=object_url)
        #db.session.query(UserScrapy).filter(UserScrapy.user_keyword_id == keyword_id).delete()
        db.session.query(UserKeyword).filter(UserKeyword.id == keyword_id).delete()
        
        db.session.commit()
    except SQLAlchemyError as e:
        flash("keyword削除処理でエラーが発生しました")
        
        current_app.logger.error(e)
        db.session.rollback()
    
    return redirect(url_for("scrapy.index"))