from fastapi import FastAPI, Form, status, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from models import *
from database import engine
from sqlmodel import Session, select
from typing import Annotated

app = FastAPI(
    description='Hotel Servise'
)

templates = Jinja2Templates('templates')

session = Session(bind=engine)




@app.get('/', response_model=Hotel, tags=['Pages'])
async def get_all_hotel(request: Request):
    statement = select(Hotel)
    result = session.exec(statement).all()
    
    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request = request,
        name = 'index.html',
        context = {
            'result': result
        }
    )

@app.get('/hotel/{Hotel_id}', response_model=Hotel, tags=['Pages'])
async def get_a_hotel(request: Request, Hotel_id: int):
    statement = select(Hotel).where(Hotel.id == Hotel_id)
    result = session.exec(statement).first()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return templates.TemplateResponse(
        request = request,
        name = 'hotel_card.html',
        context = {
            'id': result.id,
            'title': result.title,
            'price': result.price
        }
    )

@app.get('/login', tags=['Pages'])
async def get_login_page(request: Request):
    cookie = request.cookies.get('id')
    
    if cookie != None:
        return RedirectResponse('/profile/'+cookie, status_code=302)
    
    return templates.TemplateResponse('login.html', {'request': request})

@app.get('/registration', tags=['Pages'])
async def get_registration_page(request: Request):
    return templates.TemplateResponse('registration.html', {'request': request})

@app.get('/profile/{cust_id}', response_model=Customer, tags=['Pages'])
async def get_profile(request: Request, cust_id: int):
    statement = select(Customer).where(Customer.id == cust_id)
    result = session.exec(statement).first()
    

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return templates.TemplateResponse(
        request = request,
        name = 'profile.html',
        context = {
            'id': result.id,
            'first_name': result.first_name,
            'second_name': result.second_name,
            'phone': result.phone,
            'email': result.email,
            'address': result.address
        }
    )

@app.get('/cart', tags=['Pages'])
async def get_cart_page(request: Request):
    return templates.TemplateResponse(request=request, name='cart.html')




@app.post('/hotel', response_model=Hotel, status_code=status.HTTP_201_CREATED)
async def create_a_hotel(hotel: Annotated[Hotel, Depends()]):
    new_hotel = Hotel(id=hotel.id, title=hotel.title, price=hotel.price)

    session.add(new_hotel)
    session.commit()
    
    return new_hotel

@app.put('/hotel/{hotel_id}', response_model=Hotel)
async def change_a_hotel(hotel_id: int, hotel: Annotated[Hotel, Depends()]):
    statement = select(Hotel).where(Hotel.id == hotel_id)
    result = session.exec(statement).first()

    result.title = hotel.title
    result.price = hotel.price
    
    session.commit()

    return result
    
@app.delete('/hotel/{hotel_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_hotel(hotel_id: int):
    statement = select(Hotel).where(Hotel.id == hotel_id)
    result = session.exec(statement).one_or_none()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Resourse Not Found')
    
    session.delete(result)
    session.commit()

    return result




@app.post('/registration', status_code=status.HTTP_201_CREATED, 
          response_class=RedirectResponse, tags=['Account'])
async def create_a_customer(first_name: str = Form(...), 
                            second_name: str = Form(...), 
                            email: str = Form(...), 
                            address: str = Form(...),
                            phone: int = Form(...),
                            password: str = Form(...),
                            remember: Optional[bool] = Form(default=False)) -> RedirectResponse:
    
    statement = select(Customer).where(Customer.email == email or Customer.phone == phone)
    result = session.exec(statement).one_or_none()
    
    new_cust = Customer(first_name=first_name, second_name=second_name,
                        phone=phone, email=email, password=password, address=address)
    
    if result == None:
        session.add(new_cust)
        session.commit()
        
        response = RedirectResponse('/profile/'+str(new_cust.id), status_code=302)
        if remember == True:
            response.set_cookie(key="id", value=str(new_cust.id), max_age=15695000)
        return response

    return RedirectResponse('/registration', status_code=302)

@app.post('/login', response_class=RedirectResponse, tags=['Account'])
async def get_cust(email_login: str = Form(...), 
                   password_login: str = Form(...),
                   remember: Optional[bool] = Form(default=False)) -> RedirectResponse:
    email_statement = select(Customer).where(Customer.email == email_login)
    email_result = session.exec(email_statement).first()
    
    password_statement = select(Customer).where(Customer.password == password_login)
    password_result = session.exec(password_statement).first()
    
    
    if email_result != None: 
        if email_result.id == password_result.id:
            response = RedirectResponse('/profile/'+str(email_result.id), status_code=302)
            if remember == True:
                response.set_cookie(key="id", value=str(email_result.id), max_age=15695000)
            return response

@app.delete('/profile/{cust_id}', status_code=status.HTTP_204_NO_CONTENT, 
            tags=['Account'])
async def delete_a_cust(cust_id: int):
    statement = select(Customer).where(Customer.id == cust_id)
    result = session.exec(statement).one_or_none()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Resourse Not Found')
    
    session.delete(result)
    session.commit()

    return result

@app.get('/profile', tags=['Account'])
async def switch_account(response: Response):
    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie('id')
    return response



# @app.post('/')
# async def set_hotel_cookie(response: Response, id: int = Form(...), count: int = Form(...)):
#     return RedirectResponse('/id')