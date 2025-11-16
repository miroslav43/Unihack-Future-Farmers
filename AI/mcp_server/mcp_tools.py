from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware

# from mcp_server.db import serialize_datetime
from mcp_server.db import collection_weather, collection_harvest_logs, collection_farmers

import json

from datetime import datetime, timedelta

from bson import ObjectId

def serialize_datetime(dt):
    """Helper function to serialize datetime objects"""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat()
    if isinstance(dt, str):
        return dt
    return str(dt)

def serialize_objectid(obj_id):
    """Helper function to serialize ObjectId"""
    if obj_id is None:
        return None
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return obj_id

app = FastAPI()

# Add CORS middleware to the main FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],
)

mcp_weather_agent = FastMCP("Agent Weather MCP server", stateless_http=True, port=8001)
mcp_vehicles_agent = FastMCP("Agent Vehicles MCP server", stateless_http=True, port=8002)
mcp_employees_agent = FastMCP("Agent Employees MCP server", stateless_http=True, port=8003)
mcp_harvest_agent = FastMCP("Agent Harvest MCP server", stateless_http=True, port=8004)
    
@mcp_weather_agent.tool()
async def get_weather_info_for_last_n_days(number_of_days: int, today_day: int, today_month:int, today_year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the weather for the past n days, starting from
        today. This tool queries the weather database, where we have scrapped important information in this direction.

        Input: 
            type: (int), name: days, equal with n from the description above, and means the number of days to fetch the weather information from the past relative to today.
            type: (int), name: today_day, today_month, today_year represents the date (day - month - year) that we are currently in.

        Output:
            type: (dict), meaning: a mapping for the weather (temperature and possible description) for the days that have been requested when calling this tool. 
    """

    # Build the "today" date
    today = datetime(today_year, today_month, today_day)

    # Build list of date strings in format "YYYY-MM-DD"
    requested_dates = [
        (today - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(number_of_days)
    ]

    # Build query: find all documents WHERE date ∈ requested_dates
    query = {
        "date": {"$in": requested_dates}
    }

    # Convert cursor to list to avoid serialization issues
    cursor = collection_weather.find(query)
    documents = list(cursor)

    # Build response dictionary
    results = {}

    for doc in documents:
        date_key = doc.get("date")
        results[date_key] = {
            "max_temp_celsius": doc.get("max_temp_celsius"),
            "min_temp_celsius": doc.get("min_temp_celsius"),
            "weather_description": doc.get("weather_description"),
            "location": doc.get("location"),
            "temperature_unit": doc.get("temperature_unit"),
            "imported_at": serialize_datetime(doc.get("imported_at"))
            # Note: Removed _id from results since it's not needed and causes serialization issues
        }

    return results

@mcp_weather_agent.tool()
async def get_weather_info_for_the_next_n_days(days: int, today_day: int, today_month:int, today_year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the weather for the next n days (! if available !), starting from
        today. This tool queries the weather database, where we have scrapped important information in this direction.

        Input: 
            type: (int), name: days, equal with n from the description above, and means the number of days to fetch the weather information from the past relative to today.
            type: (int), name: today_day, today_month, today_year represents the date (day - month - year) that we are currently in.

        Output:
            type: (dict), meaning: a mapping for the weather (temperature and possible description) for the days that have been requested when calling this tool. 
    """

    today = datetime(today_year, today_month, today_day).strftime("%Y-%m-%d")

    # Query for dates greater than today
    query = {
        "date": {"$gt": today}
    }

    # Sort ascending (nearest dates first), limit N days
    cursor = collection_weather.find(query).sort("date", 1).limit(days)

    documents = list(cursor)

    results = {}
    for doc in documents:
        date_key = doc.get("date")
        results[date_key] = {
            "max_temp_celsius": doc.get("max_temp_celsius"),
            "min_temp_celsius": doc.get("min_temp_celsius"),
            "weather_description": doc.get("weather_description"),
            "location": doc.get("location"),
            "temperature_unit": doc.get("temperature_unit"),
            "imported_at": serialize_datetime(doc.get("imported_at")),
        }

    return results

@mcp_weather_agent.tool()
async def get_weather_info_for_a_day(day: int, month:int, year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the weather for a speciffic day. This tool queries the weather database, 
        where we have scrapped important information in this direction.

        Input: 
            type: (int), name: day, month, year represents the date (day - month - year) that we request the weather information for.

        Output:
            type: (dict), meaning: a mapping for the weather (temperature and possible description) for the date this tool was called with.
    """

    # Convert input date to string format "YYYY-MM-DD"
    requested_date = datetime(year, month, day).strftime("%Y-%m-%d")

    # Build query: find a document where date == requested_date
    query = {"date": requested_date}

    doc = collection_weather.find_one(query)

    # If nothing found → return empty dict
    if not doc:
        return {}

    # Build response
    result = {
        "date": doc.get("date"),
        "max_temp_celsius": doc.get("max_temp_celsius"),
        "min_temp_celsius": doc.get("min_temp_celsius"),
        "weather_description": doc.get("weather_description"),
        "location": doc.get("location"),
        "temperature_unit": doc.get("temperature_unit"),
        "imported_at": serialize_datetime(doc.get("imported_at")),
    }

    return result

@mcp_vehicles_agent.tool()
async def get_oil_price_for_a_specific_day(day: int, month: int, year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the oil price for a speciffic day. This tool queries a database where the oil prices are stored
        for each day found in that database. 

        Input: 
            type: (int), name: day, month, year represents the date (day - month - year) that we request the oil price information for.

        Output:
            type: (dict), meaning: a mapping for the price of 1 liter of oil to currency, based on the date this tool was called with.
    """
    target_date = datetime(year, month, day)
    query = {"date": target_date}

    doc = collection_harvest_logs.find_one(query)

    if not doc:
        return {
            "error": "No oil price data found for the given date",
            "date": target_date.isoformat()
        }

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "oil_price_per_liter": doc.get("oil_price_per_liter"),
        "currency": "RON"
    }

@mcp_vehicles_agent.tool()
async def get_total_oil_price_for_a_period_of_time(start_day: int, start_month: int, start_year: int, end_day: int, end_month: int, end_year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the total oil price for a specific period of time. This tool queries a database where the oil prices are stored
        for each day found in that database. 

        Input: 
            input variables representing the start and end dates of the period of time.

        Output:
            type: (dict), meaning: a mapping for the price of total liters of oil to currency, based on the perioad of time this tool was called with.
    """
    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    # Include entire last day
    end_date_exclusive = end_date + timedelta(days=1)

    query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date_exclusive
        }
    }

    cursor = collection_harvest_logs.find(query)

    total_fuel_consumed_liters = 0.0
    total_fuel_cost = 0.0

    for doc in cursor:
        oil_price_per_liter = doc.get("oil_price_per_liter")
        equipment_list = doc.get("equipment", [])

        if oil_price_per_liter is None or not equipment_list:
            continue

        # calculate liters consumed for this day
        daily_fuel_liters = 0.0
        for eq in equipment_list:
            liters = eq.get("fuel_consumed_liters")
            if liters is not None:
                daily_fuel_liters += float(liters)

        if daily_fuel_liters == 0:
            continue

        # calculate cost for this day
        total_fuel_cost += daily_fuel_liters * float(oil_price_per_liter)
        total_fuel_consumed_liters += daily_fuel_liters

    if total_fuel_consumed_liters == 0:
        return {
            "error": "No fuel consumption data found for the given period",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_fuel_consumed_liters": total_fuel_consumed_liters,
        "total_fuel_cost": total_fuel_cost,
        "currency": "RON"
    }

@mcp_employees_agent.tool()
async def get_employees_paid_in_n_days_from_date(n_days: int,start_day: int,start_month: int,start_year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the employees which need to be paid in n days from a specific date. This tool queries the 
        farmers database, where the employees data is stored.
        Input: 
            type: (int), name: n_days, equal with n from the description above, and means the number of days from the specific date to check which employees need to be paid.
            type: (int), name: start_day, start_month, start_year represents the date (day - month - year) that we are currently in.
        Output:
            type: (dict), meaning: a mapping for the employees which need to be paid in n days from the specific date, total amount to be paid, .

    """
    start_date = datetime(start_year, start_month, start_day)

    # 2. Interval upper bound
    end_date = start_date + timedelta(days=n_days)

    # 3. Construim lista de "day-of-month" din interval
    #    ex: 26, 27, 28, 29, 30, 31
    days_in_range = set()

    curr = start_date
    while curr <= end_date:
        days_in_range.add(curr.day)
        curr += timedelta(days=1)

    # 4. Căutăm toți cu payday în acest range
    query = {"payday": {"$in": list(days_in_range)}}

    # PyMongo e sync → nu await
    cursor = collection_farmers.find(query)

    employees = []
    for doc in cursor:
        employees.append({
            "first_name": doc.get("first_name"),
            "last_name": doc.get("last_name"),
            "cnp": doc.get("cnp"),
            "payday": doc.get("payday")
        })

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "paydays_in_range": sorted(list(days_in_range)),
        "total_employees_to_be_paid": len(employees),
        "employees": employees
    }

@mcp_employees_agent.tool()
async def get_employee_working_hours_for_a_period(first_name: str,last_name: str,start_day: int,start_month: int,
                                                                   start_year: int,end_day: int,end_month: int,end_year: int) -> dict:
    """
        Tool description:
            Tool used to get information about the number of working hours of employees for a specific period of time. This tool queries the 
        farmers database, where the employees data is stored.
        Input: 
            type: (str), first_name, last_name represents the name of the employee we want to check the working hours for.
            type: (int), name: start_day, start_month, start_year, end_day, end_month, end_year represents the period of time we want to check.
        Output:
            type: (dict), meaning: a mapping for the employees and their working hours within the specified period.

    """

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    # end_date exclusiv ca să includem toată ziua de end_date
    end_date_exclusive = end_date + timedelta(days=1)

    # 2. Căutăm angajatul după nume în collection_farmers
    farmer_query = {
        "first_name": first_name,
        "last_name": last_name
    }

    farmer_cursor = collection_farmers.find(farmer_query)

    employee_doc = None
    for doc in farmer_cursor:
        employee_doc = doc
        break  # luăm doar primul care se potrivește

    if not employee_doc:
        return {
            "error": "Employee not found",
            "first_name": first_name,
            "last_name": last_name
        }

    employee_id_str = str(employee_doc.get("_id"))

    # 3. Luăm toate harvest logs din perioada cerută
    logs_query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date_exclusive
        }
    }

    logs_cursor = collection_harvest_logs.find(logs_query)

    total_work_hours = 0.0

    # 4. Parcurgem fiecare log și fiecare equipment din el
    for log in logs_cursor:
        equipment_list = log.get("equipment", [])
        for eq in equipment_list:
            # verificăm dacă acest record de equipment e pentru angajatul nostru
            if eq.get("farmer_id") == employee_id_str:
                work_hours = eq.get("work_hours")
                if work_hours is not None:
                    total_work_hours += float(work_hours)

    # 5. Returnăm rezultatul
    return {
        "employee": {
            "first_name": employee_doc.get("first_name"),
            "last_name": employee_doc.get("last_name"),
            "cnp": employee_doc.get("cnp")
        },
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_work_hours_in_period": total_work_hours
    }

@mcp_employees_agent.tool()
async def get_employee_with_a_specific_role(role: str) -> dict:
    """
        Tool description:
            Tool used to get all employees with a specific role. This tool queries the farmers database, where the employees data is stored.
        Input: 
            type: (str), role, represents the role of the employees we want to fetch.
        Output:
            type: (dict), meaning: a mapping for the employees and a specific role.

    """
    query = {"role": role}

    # PyMongo / PyBase sync -> nu folosim await
    cursor = collection_farmers.find(query)

    employees = []
    for doc in cursor:
        employees.append({
            "first_name": doc.get("first_name"),
            "last_name": doc.get("last_name"),
            "cnp": doc.get("cnp"),
            "role": doc.get("role")
        })

    return {
        "total_employees_with_role": len(employees),
        "employees": employees
    }

@mcp_employees_agent.tool()
async def get_employees_bday_in_next_n_days_from_day_x(n:int, start_day: int,start_month: int,
                                                                   start_year: int) -> dict:
    """
        Tool description:
            Tool used to get employees birthday in next n days starting from a specific day. This tool queries the farmers database, where the employees data is stored.
        Input: 
            type: (int), n, represents the number of days from the specific date to check which employees have birthday.
            type: (int), name: start_day, start_month, start_year represents the starting date (day - month - year) that we are currently in.
        Output:
            type: (dict), meaning: a mapping for the employees and their birthdays in the next n days starting from the specific date.

    """
    start_date = datetime(start_year, start_month, start_day).date()
    end_date = start_date + timedelta(days=n)

    # 2. Construim set-ul de (month, day) pentru toate zilele din interval
    days_in_range = set()
    curr = start_date
    while curr <= end_date:
        days_in_range.add((curr.month, curr.day))
        curr += timedelta(days=1)

    # 3. Luăm toți angajații din baza de date
    cursor = collection_farmers.find({})  # PyMongo / PyBase sync → fără await

    employees = []

    for doc in cursor:
        cnp = str(doc.get("cnp", "")).strip()

        # CNP trebuie să aibă cel puțin 6 cifre pentru a extrage MM și DD
        if len(cnp) < 6:
            continue

        mm_str = cnp[3:5]  # cifrele 3-4
        dd_str = cnp[5:7]  # cifrele 5-6

        if not (mm_str.isdigit() and dd_str.isdigit()):
            continue

        month = int(mm_str)
        day = int(dd_str)

        # validare simplă
        if not (1 <= month <= 12 and 1 <= day <= 31):
            continue

        # verificăm dacă (month, day) este în intervalul nostru
        if (month, day) in days_in_range:
            employees.append({
                "first_name": doc.get("first_name"),
                "last_name": doc.get("last_name"),
                "cnp": cnp,
                "birthday_month": month,
                "birthday_day": day,
            })

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_employees_with_birthday": len(employees),
        "employees": employees,
    }

@mcp_employees_agent.tool()
async def get_stats_about_employees_tasks_from_last_n_days(n:int, start_day: int,start_month: int,
                                                                   start_year: int) -> dict:
    """
        Tool description:
            Tool used to get stats about employees tasks from last n days starting from a specific day. This tool queries the farmers database, where the employees data is stored.
        Input: 
            type: (int), n, represents the number of days from the specific date to check which employees have birthday.
            type: (int), name: start_day, start_month, start_year represents the starting date (day - month - year) that we are currently in.
        Output:
            type: (dict), meaning: a mapping for the employees and their tasks stats from the last n days starting from the specific date: how many
        employees worked per each day and which were their tasks.

    """
    end_date = datetime(start_year, start_month, start_day)
    start_date = end_date - timedelta(days=n-1)  # ex: n=7 → ultimele 7 zile
    end_date_exclusive = end_date + timedelta(days=1)

    # 2. Luăm toate harvest_logs din interval
    logs_query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date_exclusive
        }
    }
    logs_cursor = collection_harvest_logs.find(logs_query)

    # Structură intermediară:
    # days[date_str] = {
    #   "employee_tasks": { farmer_id_str: { equipment_type: total_hours } }
    # }
    days = {}
    all_employee_ids = set()

    for log in logs_cursor:
        date_value = log.get("date")
        if not date_value:
            continue

        date_str = date_value.strftime("%Y-%m-%d")
        if date_str not in days:
            days[date_str] = {"employee_tasks": {}}

        equipment_list = log.get("equipment", [])
        for eq in equipment_list:
            farmer_id_str = eq.get("farmer_id")
            equipment_type = eq.get("equipment_type", "Unknown")
            work_hours = eq.get("work_hours", 0)

            if not farmer_id_str:
                continue

            all_employee_ids.add(farmer_id_str)

            if farmer_id_str not in days[date_str]["employee_tasks"]:
                days[date_str]["employee_tasks"][farmer_id_str] = {}

            if equipment_type not in days[date_str]["employee_tasks"][farmer_id_str]:
                days[date_str]["employee_tasks"][farmer_id_str][equipment_type] = 0.0

            days[date_str]["employee_tasks"][farmer_id_str][equipment_type] += float(work_hours or 0)

    # Dacă nu a lucrat nimeni în interval
    if not days:
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "n_days": n,
            "total_unique_employees": 0,
            "daily_stats": []
        }

    # 3. Luăm info despre angajați din collection_farmers
    #    presupunem că în equipment.farmer_id este str(ObjectId(...))
    farmer_ids_as_objectid = []
    for fid in all_employee_ids:
        try:
            farmer_ids_as_objectid.append(ObjectId(fid))
        except Exception:
            # dacă nu e ObjectId valid, ignorăm (sau îl tratăm separat)
            continue

    farmers_map = {}
    if farmer_ids_as_objectid:
        farmers_cursor = collection_farmers.find({"_id": {"$in": farmer_ids_as_objectid}})
        for farmer in farmers_cursor:
            fid_str = str(farmer.get("_id"))
            farmers_map[fid_str] = {
                "first_name": farmer.get("first_name"),
                "last_name": farmer.get("last_name"),
                "role": farmer.get("role"),
                "cnp": farmer.get("cnp"),
            }

    # 4. Construim output-ul pe zile
    daily_stats = []
    for date_str in sorted(days.keys()):
        employee_tasks = days[date_str]["employee_tasks"]
        employees_out = []

        for fid_str, tasks_hours in employee_tasks.items():
            info = farmers_map.get(fid_str, {})
            
            # Calculăm totalul orelor pentru angajatul respectiv în ziua respectivă
            total_hours_for_day = sum(tasks_hours.values())
            
            # Construim lista de task-uri cu orele aferente
            tasks_list = []
            for task_type, hours in tasks_hours.items():
                tasks_list.append({
                    "equipment_type": task_type,
                    "work_hours": hours
                })
            
            employees_out.append({
                "id": fid_str,
                "first_name": info.get("first_name"),
                "last_name": info.get("last_name"),
                "role": info.get("role"),
                "cnp": info.get("cnp"),
                "tasks": tasks_list,
                "total_work_hours_for_day": total_hours_for_day
            })

        daily_stats.append({
            "date": date_str,
            "total_employees_worked": len(employees_out),
            "employees": employees_out
        })

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "n_days": n,
        "total_unique_employees": len(all_employee_ids),
        "daily_stats": daily_stats
    }

@mcp_harvest_agent.tool()
async def get_wheat_yield_for_a_specific_period(start_day: int,start_month: int,
                                                start_year: int, end_day: int, end_month: int, end_year: int) -> dict:
    """
        Tool description:
            Tool used to get wheat yield for a specific period. This tool queries the harvest_logs database, where the harvest data is stored.
        Input: 
            type: (int), name: start_day, start_month, start_year, end_day, end_month, end_year represent the period of time.
        Output:
            type: (dict), meaning: a mapping for the wheat yield within the specified period.

    """
    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    end_date_exclusive = end_date + timedelta(days=1)

    # 2. Query în harvest_logs pentru interval
    logs_query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date_exclusive
        }
    }

    # collection_harvest_logs este sync (PyMongo / PyBase style) → nu folosim await
    logs_cursor = collection_harvest_logs.find(logs_query)

    total_wheat_kg = 0.0
    total_wheat_hectares = 0.0
    daily_stats = []

    for log in logs_cursor:
        date_value = log.get("date")

        wheat_kg = float(log.get("wheat_harvested_kg", 0) or 0)
        wheat_hectares = float(log.get("wheat_harvested_hectares", 0) or 0)

        # actualizăm totalurile pe toată perioada
        total_wheat_kg += wheat_kg
        total_wheat_hectares += wheat_hectares

        # calculăm yield-ul pe zi, dacă avem hectare > 0
        if wheat_hectares > 0:
            daily_yield = wheat_kg / wheat_hectares
        else:
            daily_yield = 0.0  # sau None, daca vrei să marchezi lipsa datelor

        daily_stats.append({
            "date": date_value.strftime("%Y-%m-%d") if date_value else None,
            "wheat_harvested_kg": wheat_kg,
            "wheat_harvested_hectares": wheat_hectares,
            "wheat_yield_kg_per_hectare": daily_yield
        })

    # yield general pe toată perioada
    if total_wheat_hectares > 0:
        overall_yield = total_wheat_kg / total_wheat_hectares
    else:
        overall_yield = 0.0

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_wheat_harvested_kg": total_wheat_kg,
        "total_wheat_harvested_hectares": total_wheat_hectares,
        "overall_wheat_yield_kg_per_hectare": overall_yield,
        "daily_stats": daily_stats
    }

@mcp_harvest_agent.tool()
async def get_tomatoes_yield_for_a_specific_period(start_day: int,start_month: int,
                                                start_year: int, end_day: int, end_month: int, end_year: int) -> dict:
    """
        Tool description:
            Tool used to get tomatoes yield for a specific period. This tool queries the harvest_logs database, where the harvest data is stored.
        Input: 
            type: (int), name: start_day, start_month, start_year, end_day, end_month, end_year represent the period of time.
        Output:
            type: (dict), meaning: a mapping for the tomatoes yield within the specified period.

    """
    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    end_date_exclusive = end_date + timedelta(days=1)

    # 2. Query în harvest_logs pentru interval
    logs_query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date_exclusive
        }
    }

    # collection_harvest_logs este sync (PyMongo / PyBase style) → nu folosim await
    logs_cursor = collection_harvest_logs.find(logs_query)

    total_tomatoes_kg = 0.0
    total_tomatoes_hectares = 0.0
    daily_stats = []

    for log in logs_cursor:
        date_value = log.get("date")

        tomatoes_kg = float(log.get("tomatoes_harvested_kg", 0) or 0)
        tomatoes_hectares = float(log.get("tomatoes_harvested_hectares", 0) or 0)

        # actualizăm totalurile pe toată perioada
        total_tomatoes_kg += tomatoes_kg
        total_tomatoes_hectares += tomatoes_hectares

        # calculăm yield-ul pe zi, dacă avem hectare > 0
        if tomatoes_hectares > 0:
            daily_yield = tomatoes_kg / tomatoes_hectares
        else:
            daily_yield = 0.0  # sau None, daca vrei să marchezi lipsa datelor

        daily_stats.append({
            "date": date_value.strftime("%Y-%m-%d") if date_value else None,
            "tomatoes_harvested_kg": tomatoes_kg,
            "tomatoes_harvested_hectares": tomatoes_hectares,
            "tomatoes_yield_kg_per_hectare": daily_yield
        })

    # yield general pe toată perioada
    if total_tomatoes_hectares > 0:
        overall_yield = total_tomatoes_kg / total_tomatoes_hectares
    else:
        overall_yield = 0.0

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_tomatoes_harvested_kg": total_tomatoes_kg,
        "total_tomatoes_harvested_hectares": total_tomatoes_hectares,
        "overall_tomatoes_yield_kg_per_hectare": overall_yield,
        "daily_stats": daily_stats
    }

@mcp_harvest_agent.tool()
async def get_sunflower_yield_for_a_specific_period(start_day: int,start_month: int,
                                                start_year: int, end_day: int, end_month: int, end_year: int) -> dict:
    """
        Tool description:
            Tool used to get sunflower yield for a specific period. This tool queries the harvest_logs database, where the harvest data is stored.
        Input: 
            type: (int), name: start_day, start_month, start_year, end_day, end_month, end_year represent the period of time.
        Output:
            type: (dict), meaning: a mapping for the sunflower yield within the specified period.

    """
    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    end_date_exclusive = end_date + timedelta(days=1)

    # 2. Query în harvest_logs pentru interval
    logs_query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date_exclusive
        }
    }

    # collection_harvest_logs este sync (PyMongo / PyBase style) → nu folosim await
    logs_cursor = collection_harvest_logs.find(logs_query)

    total_sunflower_kg = 0.0
    total_sunflower_hectares = 0.0
    daily_stats = []

    for log in logs_cursor:
        date_value = log.get("date")

        sunflower_kg = float(log.get("sunflower_harvested_kg", 0) or 0)
        sunflower_hectares = float(log.get("sunflower_harvested_hectares", 0) or 0)

        # actualizăm totalurile pe toată perioada
        total_sunflower_kg += sunflower_kg
        total_sunflower_hectares += sunflower_hectares

        # calculăm yield-ul pe zi, dacă avem hectare > 0
        if sunflower_hectares > 0:
            daily_yield = sunflower_kg / sunflower_hectares
        else:
            daily_yield = 0.0  # sau None, daca vrei să marchezi lipsa datelor

        daily_stats.append({
            "date": date_value.strftime("%Y-%m-%d") if date_value else None,
            "sunflower_harvested_kg": sunflower_kg,
            "sunflower_harvested_hectares": sunflower_hectares,
            "sunflower_yield_kg_per_hectare": daily_yield
        })

    # yield general pe toată perioada
    if total_sunflower_hectares > 0:
        overall_yield = total_sunflower_kg / total_sunflower_hectares
    else:
        overall_yield = 0.0

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_sunflower_harvested_kg": total_sunflower_kg,
        "total_sunflower_harvested_hectares": total_sunflower_hectares,
        "overall_sunflower_yield_kg_per_hectare": overall_yield,
        "daily_stats": daily_stats
    }

@mcp_harvest_agent.tool()
async def get_beans_yield_for_a_specific_period(start_day: int,start_month: int,
                                                start_year: int, end_day: int, end_month: int, end_year: int) -> dict:
    """
        Tool description:
            Tool used to get beans yield for a specific period. This tool queries the harvest_logs database, where the harvest data is stored.
        Input: 
            type: (int), name: start_day, start_month, start_year, end_day, end_month, end_year represent the period of time.
        Output:
            type: (dict), meaning: a mapping for the beans yield within the specified period.

    """
    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)
    end_date_exclusive = end_date + timedelta(days=1)

    # 2. Query în harvest_logs pentru interval
    logs_query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date_exclusive
        }
    }

    # collection_harvest_logs este sync (PyMongo / PyBase style) → nu folosim await
    logs_cursor = collection_harvest_logs.find(logs_query)

    total_beans_kg = 0.0
    total_beans_hectares = 0.0
    daily_stats = []

    for log in logs_cursor:
        date_value = log.get("date")

        beans_kg = float(log.get("beans_harvested_kg", 0) or 0)
        beans_hectares = float(log.get("beans_harvested_hectares", 0) or 0)

        # actualizăm totalurile pe toată perioada
        total_beans_kg += beans_kg
        total_beans_hectares += beans_hectares

        # calculăm yield-ul pe zi, dacă avem hectare > 0
        if beans_hectares > 0:
            daily_yield = beans_kg / beans_hectares
        else:
            daily_yield = 0.0  # sau None, daca vrei să marchezi lipsa datelor

        daily_stats.append({
            "date": date_value.strftime("%Y-%m-%d") if date_value else None,
            "beans_harvested_kg": beans_kg,
            "beans_harvested_hectares": beans_hectares,
            "beans_yield_kg_per_hectare": daily_yield
        })

    # yield general pe toată perioada
    if total_beans_hectares > 0:
        overall_yield = total_beans_kg / total_beans_hectares
    else:
        overall_yield = 0.0

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_beans_harvested_kg": total_beans_kg,
        "total_beans_harvested_hectares": total_beans_hectares,
        "overall_beans_yield_kg_per_hectare": overall_yield,
        "daily_stats": daily_stats
    }

@mcp_harvest_agent.tool()
async def get_harvest_stats_with_a_specific_note(note: str) -> dict:
    """
        Tool description:
            Tool used to get harvest stats with a specific note(each day with a certain note). This tool queries the harvest_logs database, where the harvest data is stored.
        Input: 
            type: (str), name: note, representing the specific note to filter harvest stats.
        Output:
            type: (dict), meaning: a mapping for the harvest stats that contain the specific note.

    """
    query = {"notes": note}  # câmpul tău în exemple e 'notes': "Normal", "Weekend", etc.
    cursor = collection_harvest_logs.find(query)

    daily_stats = []

    total_beans_kg = 0.0
    total_sunflower_kg = 0.0
    total_tomatoes_kg = 0.0
    total_wheat_kg = 0.0

    total_beans_hectares = 0.0
    total_sunflower_hectares = 0.0
    total_tomatoes_hectares = 0.0
    total_wheat_hectares = 0.0

    total_days = 0

    for log in cursor:
        date_value = log.get("date")

        beans_kg = float(log.get("beans_harvested_kg", 0) or 0)
        sunflower_kg = float(log.get("sunflower_harvested_kg", 0) or 0)
        tomatoes_kg = float(log.get("tomatoes_harvested_kg", 0) or 0)
        wheat_kg = float(log.get("wheat_harvested_kg", 0) or 0)

        beans_hectares = float(log.get("beans_harvested_hectares", 0) or 0)
        sunflower_hectares = float(log.get("sunflower_harvested_hectares", 0) or 0)
        tomatoes_hectares = float(log.get("tomatoes_harvested_hectares", 0) or 0)
        wheat_hectares = float(log.get("wheat_harvested_hectares", 0) or 0)

        # actualizăm totalurile
        total_beans_kg += beans_kg
        total_sunflower_kg += sunflower_kg
        total_tomatoes_kg += tomatoes_kg
        total_wheat_kg += wheat_kg

        total_beans_hectares += beans_hectares
        total_sunflower_hectares += sunflower_hectares
        total_tomatoes_hectares += tomatoes_hectares
        total_wheat_hectares += wheat_hectares

        total_days += 1

        daily_stats.append({
            "date": date_value.strftime("%Y-%m-%d") if date_value else None,
            "beans_harvested_kg": beans_kg,
            "sunflower_harvested_kg": sunflower_kg,
            "tomatoes_harvested_kg": tomatoes_kg,
            "wheat_harvested_kg": wheat_kg,
            "beans_harvested_hectares": beans_hectares,
            "sunflower_harvested_hectares": sunflower_hectares,
            "tomatoes_harvested_hectares": tomatoes_hectares,
            "wheat_harvested_hectares": wheat_hectares,
        })

    total_all_crops_kg = total_beans_kg + total_sunflower_kg + total_tomatoes_kg + total_wheat_kg

    return {
        "note": note,
        "total_days_with_note": total_days,
        "total_harvested_kg": {
            "beans": total_beans_kg,
            "sunflower": total_sunflower_kg,
            "tomatoes": total_tomatoes_kg,
            "wheat": total_wheat_kg,
            "all_crops": total_all_crops_kg,
        },
        "total_harvested_hectares": {
            "beans": total_beans_hectares,
            "sunflower": total_sunflower_hectares,
            "tomatoes": total_tomatoes_hectares,
            "wheat": total_wheat_hectares,
        },
        "daily_stats": daily_stats
    }

# npx @modelcontextprotocol/inspector
# uvicorn mcp_server.mcp_tools:app --host 0.0.0.0 --port 8000

# ====== Mount the 3 servers ======
asyncio.gather(mcp_weather_agent.run_streamable_http_async(), mcp_vehicles_agent.run_streamable_http_async(), 
mcp_employees_agent.run_streamable_http_async(),mcp_harvest_agent.run_streamable_http_async())

app.mount("/mcp/mcp_weather_agent", mcp_weather_agent.streamable_http_app())
app.mount("/mcp/mcp_vehicles_agent", mcp_vehicles_agent.streamable_http_app())
app.mount("/mcp/mcp_employees_agent", mcp_employees_agent.streamable_http_app())
app.mount("/mcp/mcp_harvest_agent", mcp_harvest_agent.streamable_http_app())