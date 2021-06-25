import os
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

# DATABASE_URL = 'postgres://kiufnyzelvojho:331c381b46dc08c8ac85cdf5fd022c4abbf7424baa66cbeec6589739a8ec2702@ec2-176-34-105-15.eu-west-1.compute.amazonaws.com:5432/de49s33kdavj49'

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# method 2

DATABASE_URL = 'postgresql://sugxbwhqwfvbgq:c942aa329688760e53e3b39fe0f0e48ca580b0e919378c656c7c3b441eef1bca@ec2-54-228-9-90.eu-west-1.compute.amazonaws.com:5432/d226jg5evs5g3o'

engine = create_engine(DATABASE_URL, echo=False)


df = pd.DataFrame({'name' : ['User 1', 'User 2', 'User 3']})

df.to_sql('users', con=engine)

res = engine.execute("SELECT * FROM users").fetchall()