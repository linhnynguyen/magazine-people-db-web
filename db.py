from flask import Flask, render_template, request, redirect, url_for, session, Response
import psycopg2
import psycopg2.extras
import os

def connect():
    conn = psycopg2.connect(
    host = 'sqledu.univ-eiffel.fr',
    port = "5432",
    user='achille.navarro',
    password='Tempouni4498//',
    dbname = 'achille.navarro_db',
    #cursor_factory = psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn