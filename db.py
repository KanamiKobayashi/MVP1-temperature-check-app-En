import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


def select_all(con):
    """ SELECTする """
    cur = con.execute('select id, student_name, temperature, parent_id, input_date, modified_by, check_date, created from results order by id desc')
    return cur.fetchall()
 
def select_all_users(con):
    """ SELECTする """
    cur = con.execute('select id, username, role from user order by id desc')
    return cur.fetchall()

def select(con, pk):
    """ 指定したキーのデータをSELECTする """
    cur = con.execute('select id, student_name, temperature, parent_id, input_date, modified_by, check_date, created from results where id=?', (pk,))
    return cur.fetchone()
 
 
def insert(con, student_name, temperature, parent_id, input_date, modified_by, check_date):
    """ INSERTする """
    cur = con.cursor()
    cur.execute('insert into results (student_name, temperature, parent_id, input_date, modified_by, check_date) values (?, ?, ?, ?, ?, ?)', [student_name, temperature, parent_id, input_date, modified_by, check_date])
    pk = cur.lastrowid
    con.commit()
    return pk
 
def delete(con, pk):
    """ 指定したキーのデータをDELETEする """
    cur = con.cursor()
    cur.execute('delete from results where id=?', (pk,))
    con.commit()
 