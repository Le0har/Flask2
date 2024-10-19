from api import app, db, multi_auth
from api.models.user import UserModel


@app.route('/auth/token')
@multi_auth.login_required
def get_auth_token():
    username = multi_auth.current_user()
    user = db.one_or_404(db.select(UserModel).filter_by(name=username))
    token = user.generate_auth_token()
    return {'token': token}
