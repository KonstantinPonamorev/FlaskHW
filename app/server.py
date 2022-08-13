import pydantic
import typing
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, create_engine
from flask_bcrypt import Bcrypt


def hash_password(password: str):
    password = password.encode()
    hashed = bcrypt.generate_password_hash(password)
    return hashed.decode()


class HttpError(Exception):

    def __init__(self, status_code: int, message: str or dict or list):
        self.status_code = status_code
        self.message = message


class CreateUser(pydantic.BaseModel):
    name: str
    password: str


class PatchUser(pydantic.BaseModel):
    name: typing.Optional[str]
    password: typing.Optional[str]


class CreateAdvertisement(pydantic.BaseModel):
    header: str
    description: str
    owner_id: int


class PatchAdvertisement(pydantic.BaseModel):
    header: typing.Optional[str]
    description: typing.Optional[str]


def validate(model, raw_data: dict):
    try:
        return model(**raw_data).dict()
    except pydantic.ValidationError as error:
        raise HttpError(400, error.errors())


app = Flask('app')
bcrypt = Bcrypt(app)


@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    response = jsonify({
        'status': 'error',
        'reason': error.message
    })
    response.status_code = error.status_code
    return response


PG_DSN = 'postgresql://app:1234@127.0.0.1/flask'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Advertisement(Base):

    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True)
    header = Column(String, index=True, unique=True, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))


def get_object(object_class, session: Session, object_id: int):
    item = session.query(object_class).get(object_id)
    if item is None:
        raise HttpError(404, 'object not found')
    return item


Base.metadata.create_all(engine)


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = get_object(User, session, user_id)
            return jsonify({'name': user.name})

    def post(self):
        validated = validate(CreateUser, request.json)
        with Session() as session:
            user = User(name=validated['name'],
                        password=hash_password(validated['password']))
            session.add(user)
            session.commit()
            return {'id': user.id}

    def patch(self, user_id):
        validated = validate(PatchUser, request.json)
        with Session() as session:
            user = get_object(User, session, user_id)
            if validated.get('name'):
                user.name = validated['name']
            if validated.get('password'):
                user.password = hash_password(validated['password'])
            session.add(user)
            session.commit()
            return {
                'status': 'success',
                'name': user.name
            }

    def delete(self, user_id):
        with Session() as session:
            user = get_object(User, session, user_id)
            session.delete(user)
            session.commit()
            return {'status': 'success'}


user_view = UserView.as_view('users')
app.add_url_rule('/users/', view_func=user_view, methods=['POST'])
app.add_url_rule('/users/<int:user_id>', view_func=user_view, methods=['GET', 'PATCH', 'DELETE'])


class AdvertisementView(MethodView):

    def get(self, advertisement_id):
        with Session() as session:
            advertisement = get_object(Advertisement, session, advertisement_id)
            return jsonify({'header': advertisement.header,
                            'description': advertisement.description,
                            'created_at': advertisement.created_at.isoformat(),
                            'owner_id': advertisement.owner_id})

    def post(self):
        validated = validate(CreateAdvertisement, request.json)
        with Session() as session:
            advertisement = Advertisement(
                header=validated['header'],
                description=validated['description'],
                owner_id=validated['owner_id']
            )
            session.add(advertisement)
            session.commit()
            return {'id': advertisement.id}

    def patch(self, advertisement_id):
        validated = validate(PatchAdvertisement, request.json)
        with Session() as session:
            advertisement = get_object(Advertisement, session, advertisement_id)
            if validated.get('header'):
                advertisement.header = validated['header']
            if validated.get('description'):
                advertisement.description = validated['description']
            session.add(advertisement)
            session.commit()
            return {
                'status': 'success',
                'header': advertisement.header,
                'description': advertisement.description
            }

    def delete(self, advertisement_id):
        with Session() as session:
            advertisement = get_object(Advertisement, session, advertisement_id)
            session.delete(advertisement)
            session.commit()
            return {'status': 'success'}


advertisement_view = AdvertisementView.as_view('advertisements')
app.add_url_rule('/advertisements/', view_func=advertisement_view, methods=['POST'])
app.add_url_rule('/advertisements/<int:advertisement_id>', view_func=advertisement_view,
                 methods=['GET', 'PATCH', 'DELETE'])


app.run()
