from passlib.context import CryptContext
# in order to use passlib, need to install bcrypt==4.0.1 - not newest, because it isn't compatibile
# https://github.com/pyca/bcrypt/issues/684

pwd_cxt = CryptContext(schemes=['bcrypt'], deprecated='auto')

class Hash():
  def bcrypt(password: str):
    return pwd_cxt.hash(password)

  def verify(hashed_password, plain_password):
    return pwd_cxt.verify(plain_password, hashed_password)