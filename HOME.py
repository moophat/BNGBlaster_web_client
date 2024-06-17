import streamlit as st
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from lxml import etree
import argparse
import string
import os, re
import time
import requests
import json, yaml
import subprocess
from io import StringIO
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import streamlit_authenticator as stauth
from streamlit_ace import st_ace
from streamlit_authenticator.utilities.hasher import Hasher
from streamlit_tree_select import tree_select #pip install streamlit-tree-select
st.set_page_config(layout= 'wide', page_title= 'BNG Blaster', page_icon= ':cityscape:')
font_css = """
<style>
button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
  font-size: 17px;
}
# </style>
# """
st.markdown(font_css, unsafe_allow_html=True)

if 'p1' not in st.session_state:
    st.session_state.p1= True
    st.session_state.p2= False
    st.session_state.p3= False
    st.session_state.p4= False
    st.session_state.p5= False
    st.session_state.user = ''

# Function for log action
def log_authorize(user, action):
    from datetime import datetime, timezone, timedelta # Datetime
    timestamp = datetime.now(timezone(timedelta(hours=+7), 'ICT')).strftime("%d/%m/%Y_%H:%M:%S")
    with open('auth.log', 'a') as session:
        session.write('\n')
        session.write(f"{timestamp}_{user} : {action}")

# hashed_passwords = Hasher(['xxx']).generate()
# print(hashed_passwords)
import yaml
from yaml.loader import SafeLoader
with open('authen/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
colx, coly, colz = st.columns([1,1.8,1])
with coly:
    st.image('./images/home.png', output_format= 'JPEG')
    name, authentication_status, username = authenticator.login('main', fields = {'Form name': ':pushpin: :orange[LOGIN]'})
if authentication_status:
    st.session_state.user= username
    # authenticator.logout('Logout', 'main')
elif authentication_status == False:
    with coly:
        st.error('Username/password is incorrect')
        st.stop()
elif authentication_status == None:
    with coly:
        st.warning('Please enter your username and password')
        st.stop()

# from streamlit_google_auth import Authenticate

# st.title('Streamlit Google Auth Example')

# authenticator = Authenticate(
#     secret_credentials_path = 'google_credentials.json',
#     cookie_name='my_cookie_name',
#     cookie_key='this_is_secret',
#     redirect_uri = 'http://10.98.12.70:8501',
# )

# # Catch the login event
# authenticator.check_authentification()

# # Create the login button
# authenticator.login()

# if st.session_state['connected']:
#     st.image(st.session_state['user_info'].get('picture'))
#     st.write('Hello, '+ st.session_state['user_info'].get('name'))
#     st.write('Your email is '+ st.session_state['user_info'].get('email'))
#     if st.button('Log out'):
#         authenticator.logout()
########################### Functions SQLite ########################
import sys
sys.path.append('../')
from lib import *

# def create_table(conn, table_name, columns):
#     cursor = conn.cursor()
#     # Construct the CREATE TABLE SQL statement
#     columns_with_types = ', '.join(f"{col_name} {data_type}" for col_name, data_type in columns.items())
#     create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"
#     cursor.execute(create_table_sql)
#     conn.commit()
#     print(f"Table '{table_name}' created successfully.")
# table_name = 'blasters'
# columns = {
#     'ip': 'TEXT PRIMARY KEY NOT NULL',
#     'port': 'INTEGER NOT NULL',
#     'user': 'TEXT NOT NULL',
#     'passwd': 'TEXT NOT NULL'
# }
# db_name = 'blaster.db'
# conn = sqlite_connect_to_db(db_name)
# # Create table
# create_table(conn, table_name, columns)

############# Collect to DB and save to varriable ###################################
user_privilege = ['admin', 'admin1', 'operator']
db_name = 'blaster.db'
conn_db = sqlite_connect_to_db(db_name)
dict_user_db = dict(sqlite_fetch_table(conn_db, 'users'))
dict_blaster_db = pd.DataFrame(sqlite_fetch_table(conn_db, 'blasters')).to_dict('index')
dict_blaster_db_format ={}
for i in range(len(dict_blaster_db.keys())):
    element = {'port': dict_blaster_db[i][1], 'user': dict_blaster_db[i][2], 'passwd': dict_blaster_db[i][3]}
    dict_blaster_db_format[dict_blaster_db[i][0]] = element
conn_db.close()
# sqlite_create_table_user(conn)
# sqlite_insert_user(conn, 'hoanguyen', 'admin1')
# sqlite_insert_user(conn, 'linhnt', 'admin')
# users = sqlite_fetch_users(conn)
# st.write(users)
# sqlite_delete_user(conn, 'linhnt')
# users = sqlite_fetch_users(conn)
# st.write(users)
# conn.close()
#############################################################################
import ipaddress
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
################### Function for set background ############################
import base64
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .main {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-attachment: local;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
# set_background('background.jpg')

##################### Function for gif file #################################
@st.cache_resource
def gif(gif_path):
    import base64
    file_ = open(gif_path, "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/gif;base64,{data_url}" alt="cat gif" style="max-width: 100%; height: 250px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    # st.markdown(
    #     f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    #     unsafe_allow_html=True,
    # )
#############################################################################

path_bgp_update="/home/juniper/bngblaster/bgp_update"
path_configs="/home/juniper/bngblaster/configs"
path_templates="/home/juniper/bngblaster/templates"
path_templates_part="/home/juniper/bngblaster/templates_part"
path_templates_streams="/home/juniper/bngblaster/templates_streams"
path_templates_interfaces="/home/juniper/bngblaster/templates_interfaces"

payload_command_session_counters="""
{
    "command": "session-counters"
}
"""
payload_command_network_interface="""
{
    "command": "network-interfaces"
}
"""
payload_command_access_interface="""
{
    "command": "access-interfaces"
}
"""
payload_start="""
{
    "logging": true,
    "logging_flags": [
        "session",
        "stream",
        "debug",
        "pppoe",
        "ip"
    ],
    "report": true,
    "report_flags": [
        "sessions",
        "streams"
    ]
}
"""
payload_stop="""
{
    "logging": true,
    "logging_flags": [
        "session",
        "stream",
        "debug",
        "pppoe",
        "ip"
    ],
    "report": true
    "report_flags": [
        "sessions",
        "streams"
   ]
}
"""
def push_file_to_server_by_ftp(hostname, username, password, local_path, remote_path):
    import paramiko
    # Define the SFTP connection parameters
    # hostname = ''
    port = 22
    # username = ''
    # password = ''

    # Define the local file path and the remote destination path
    # local_path = '/path/to/local/file.txt'
    # remote_path = '/path/to/remote/destination/file.txt'

    # Establish an SSH transport and SFTP session
    transport = paramiko.Transport((hostname, port))
    try:
        transport.connect(username=username, password=password)
    except Exception as e:
        print(f'Error connect to server, Error: {e}')
    sftp = paramiko.SFTPClient.from_transport(transport)
    # Upload the file
    sftp.put(local_path, remote_path)
    # Close the SFTP session and the SSH transport
    sftp.close()
    transport.close()

def push_file_to_server_rest_api(server, port, file_path):
    import requests
    # Replace 'http://your-server-url.com/upload' with the actual URL of your server endpoint
    url = f'http://{server}:{port}/upload'

    # Path to the file you want to send
    # file_path = '/home/juniper/python/data.csv'

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Send a POST request with the file attached
        response = requests.post(url, files={'file': file})

    # Check the response
    if response.status_code == 200:
        print("File uploaded successfully.")
        return 200
    else:
        print("Error occurred while uploading file:", response.status_code)
def delete_file_on_server(server, port, file_path):
    import requests

    url = f'http://{server}:{port}/delete'

    # Make a POST request to the server to delete the file
    response = requests.post(url, data={'filename': file_path})

    # Check the response
    if response.status_code == 200:
        print("File deleted successfully.")
    elif response.status_code == 404:
        print("File not found on the server.")
    else:
        print("Error occurred while deleting file:", response.status_code)

def get_variables_jinja_file(file_path):
    from jinja2 import Environment, meta
    # linhnt : 24.04.2024
    # file_path : directory to folder have file
    import re
    with open(file_path, 'r') as file:
        template_content = file.read()
        # Use a regular expression to find Jinja variable syntax
        # variable_pattern = r'{{\s*(\w+)\s*}}'
        # variables = re.findall(variable_pattern, template_content)
        env = Environment() 
        parsed_content = env.parse(template_content) # Parse the template into an AST
        undeclared_variables = meta.find_undeclared_variables(parsed_content) # Find all undeclared variables
        # return list(dict.fromkeys(variables))
        return list(undeclared_variables)


def get_list_file(file_path, file_type):
  file_list=[]
  list_file_result=[]
  for files in os.walk(file_path):
      file_list = files[2] #Get file_list
  
  for i in range(len(file_list)):
    str = "^.*\." + file_type + "$"
    x= re.search(str,file_list[i])
    if x:
        list_file_result.append(file_list[i])
  #list_file_result_str = [str(x) for x in list_file_result]     # Change string format
  return list_file_result
########################## Get list config ############################################
list_json= get_list_file(path_configs, 'json') # Get list file json from folder
list_instance=[]
for i in list_json:
    list_instance.append(i.split('.')[0])
################# Get list part_template ##########################################
list_part_file= get_list_file(path_templates_part, "j2")
list_part=[]
for i in list_part_file:
    list_part.append(i[:-3])
dict_element_config={}
for i in list_part:
    # data = yaml.load(open(f"{path_templates_part}/{i}.j2", 'r'), Loader=yaml.FullLoader)
    with open(f"{path_templates_part}/{i}.j2", 'r') as part:
        data=part.read()
    dict_element_config[i] = data
# st.write(dict_element_config)
################# Get list templates_streams ##########################################
list_streams_file= get_list_file(path_templates_streams, "j2")
list_streams=[]
for i in list_streams_file:
    list_streams.append(i[:-3])
dict_streams_templates={}
for i in list_streams:
    with open(f"{path_templates_streams}/{i}.j2", 'r') as part:
        data=part.read()
    dict_streams_templates[i] = data
# st.write(dict_streams_templates)
################# Get list templates_interfaces ##########################################
list_interfaces_file= get_list_file(path_templates_interfaces, "j2")
list_interfaces=[]
for i in list_interfaces_file:
    list_interfaces.append(i[:-3])
dict_interfaces_templates={}
for i in list_interfaces:
    with open(f"{path_templates_interfaces}/{i}.j2", 'r') as part:
        data=part.read()
    dict_interfaces_templates[i] = data
# st.write(dict_interfaces_templates)
###################################################################################
list_templates= get_list_file(path_templates, 'j2') # Get list file j2 from folder
###################################################################################
list_bgp_update= get_list_file(path_bgp_update, 'bgp') # Get list file bgp from folder

def execute_remote_command(host, username, command):
    ssh_command = ['ssh', f'{username}@{host}', command]
    result = subprocess.run(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        return result.stdout.strip()  # Return the output of the command
    else:
        print(f"Error executing command: {result.stderr.strip()}")
        return None
def execute_remote_command_use_passwd(host, username, passwd , command):
    import pexpect
    ssh_command = f"ssh {username}@{host} {command}"
    child = pexpect.spawn(ssh_command, encoding='utf-8')
    # child.expect("(yes/no/[fingerprint])?")
    # child.sendline('yes')
    # child.expect("password:")
    child.sendline(passwd)
    # Capture the output
    child.expect(pexpect.EOF)
    output = child.before.splitlines()
    # print(output)
    filtered_output = [line for line in output if "@" not in line.lower()]
    if len(filtered_output) > 1:
        return filtered_output[1]
    else:
        return filtered_output[0]
def find_sub_interface(host, username, password, interface):
    sub=''
    host = '10.99.94.2'
    username = 'root'
    command = 'netstat -i | grep %s'%interface  # Command to execute remotely
    output = execute_remote_command(host, username, command)
    if output is not None:
        print("Output of the remote command:")
        line= output.split('\n')
        sub= line[-1].split(' ')[0]
        # print(sub.split('.'))
        if sub.split('.') == interface:
            return sub.split('.')[1]
        else:
            return 0
    else:
        print('Do not have already sub-interface')
        return 0
def find_interface(hostname, username, password):
    import paramiko
    # Create an SSH client
    client = paramiko.SSHClient()
    # Automatically add untrusted hosts (not recommended for production)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the remote server
        client.connect(hostname, username=username, password=password)
        # Execute the command to check network interfaces
        stdin, stdout, stderr = client.exec_command('netstat -i | grep ens')
        # Read the command output
        output = stdout.read().decode()
        error = stderr.read().decode()
        if output:
            # st.code(output)  
            line = output.split('\n')
            list_int_temp = []
            for i in line:
                sub= i.split(' ')[0]
                if ("." not in sub) and (sub != ""):
                    list_int_temp.append(sub) 
            return set(list_int_temp)          
        if error:
            print(error)
    finally:
        # Close the connection
        client.close()
def filter_dict(data: dict, extract):
    try:
        if isinstance(extract, list):
            list_result=[]
            while extract:
                if result := filter_dict(data, extract.pop(0)):
                    list_result.append(result)
            return list_result
        shadow_data = data.copy()
        for key in extract.split('.'):
            if str(key).isnumeric():
                key = int(key)
            shadow_data = shadow_data[key]
        return shadow_data
    except (IndexError, KeyError, AttributeError, TypeError):
        return None
@st.experimental_dialog("Confirmation")
def delete_config(path_configs, instance):
    st.write(f":orange[Are you sure for deleting?]")
    col1, col2 = st.columns([1,6])
    with col1:
        if st.button(":red[**YES**]"):
            os.remove(f"{path_configs}/{instance}.json")
            os.remove(f"{path_configs}/{instance}.yml")
            if os.path.exists('%s/%s_streams.yml'%(path_configs,instance)):
                os.remove(f"{path_configs}/{instance}_streams.yml")
            if os.path.exists('%s/%s_interfaces.yml'%(path_configs,instance)):
                os.remove(f"{path_configs}/{instance}_interfaces.yml")
            st.toast(':blue[Delete instance %s successfully]'%instance, icon="🔥")
            log_authorize(st.session_state.user, f'DELETE instance {instance}')
            time.sleep(1)
            st.rerun()
    with col2:
        if st.button("**CANCEL**", type= 'primary'):
            st.rerun()

# @st.cache_data
def CALL_API_BLASTER(server,port,instance, method, body, action=''):
    try:
        # print(f'http://{server}:{port}/api/v1/instances/{instance}{action}')
        response = requests.request(method, f'http://{server}:{port}/api/v1/instances/{instance}{action}', headers={'Content-Type': 'application/json'},data=body)
        # print(response.headers["Date"])
        return response.status_code, response.content
    except Exception as e:
        print(f'Can not request API blaster server. Error {e}')
def GET_ALL_INTANCES_BLASTER(server,port):
    try:
        # print(f'http://{server}:{port}/api/v1/instances/{instance}{action}')
        response = requests.request("GET", f'http://{server}:{port}/api/v1/instances', headers={'Content-Type': 'application/json'},data="")
        # print(response.headers["Date"])
        return response.status_code, response.content
    except Exception as e:
        print(f'Can not request API blaster server. Error {e}')
################## Function for blaster-status ############################################
def blaster_status(ip, port, list_instance_running_from_blaster, list_instance_avail_from_blaster):
    with st.container(border=True):
        st.subheader(f':sunny: :green[BNG-BLASTER [{ip}] STATUS]')
        col_select, col_display= st.columns([2.5,5])
        with col_select:
            with st.container(border=True, height= 300):
                st.write(":fire: :violet[**INSTANCE RUNNING**]")
                select_running_instance={}
                for i in list_instance_running_from_blaster:
                    exec(f"""select_running_instance['{i}'] = st.checkbox(f"*{i}*")""") 
                select_running_instance_cb = [] # List select checkbox
                for i in select_running_instance.keys():
                    if select_running_instance[i]:
                        select_running_instance_cb.append(i)      
        with  st.expander(":white_check_mark: :violet[**INSTANCE EXISTED CONFIG**]"):
            for i in list_instance_avail_from_blaster:
                with st.container(border=True):
                    col1, col2= st.columns([2,1])
                    with col1:
                        st.write(f":orange[**Instance :**] *{i}*")
                    with col2:
                        with st.popover(f":green[CONFIG EXISTED]", use_container_width=True):
                            view_config_avail_sc,  view_config_avail_ct = CALL_API_BLASTER(ip, port, i, 'GET', payload_start, '/config.json')
                            if view_config_avail_sc==200:
                                config_avail = json.loads(view_config_avail_ct)
                                st.write(config_avail)
                # st.dataframe(list_instance_avail_from_blaster, use_container_width= True)
                # st.dataframe(list_instance_avail_from_blaster, use_container_width= True, column_config={"value": "instance-name"})
        with col_display:
            with st.container(border=True, height= 300):
                st.write(":fire: :violet[**GRAPH**]")
                for i in select_running_instance_cb:
                    with st.popover(f":chart: *{i}*", use_container_width=True):
                        df_nw_tx_rx = pd.DataFrame([[0, 0]], columns=(["network_tx_packets", "network_rx_packets"]))
                        df_acc_tx_rx = pd.DataFrame([[0, 0]], columns=(["access_tx_packets", "access_rx_packets"]))
                        df_pktloss = pd.DataFrame([[0, 0]], columns=(["network_interface_pkt_loss", "access_interface_pkt_loss"]))
                        with st.container(border= True):
                            st.write(':orange[**NETWORK INTERFACE**]')
                            exec(f'nw_int_chart_{i} = st.line_chart(df_nw_tx_rx, color = ["#FF0000", "#0000FF"], use_container_width= True)')
                        with st.container(border= True):
                            st.write(':orange[**ACCESS INTERFACE**]')
                            exec(f'acc_int_chart_{i} = st.line_chart(df_acc_tx_rx, color = ["#FF0000", "#0000FF"], use_container_width= True)')
                        with st.container(border= True):
                            st.write(':orange[**PACKET LOSS**]')
                            exec(f'pktloss_chart_{i} = st.line_chart(df_pktloss, color = ["#FF0000", "#0000FF"],use_container_width= True)')
                if len(select_running_instance_cb) !=0:
                    while True:
                        for i in select_running_instance_cb:
                            # run_command_counter_sc, run_command_counter_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_session_counters, '/_command')
                            run_command_nw_int_sc, run_command_nw_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_network_interface, '/_command')
                            run_command_acc_int_sc, run_command_acc_int_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'POST', payload_command_access_interface, '/_command')
                            # data_counter = json.loads(run_command_counter_ct)
                            data_nw_int = json.loads(run_command_nw_int_ct)
                            # st.code(data_nw_int)
                            data_acc_int = json.loads(run_command_acc_int_ct)
                            if run_command_nw_int_sc == 200:
                                add_nw_df = pd.DataFrame([[filter_dict(data_nw_int, 'network-interfaces.0.tx-packets'), filter_dict(data_nw_int, 'network-interfaces.0.rx-packets')]], columns=(["network_tx_packets", "network_rx_packets"]))
                                eval(f'nw_int_chart_{i}.add_rows(add_nw_df)')

                                add_acc_df = pd.DataFrame([[filter_dict(data_acc_int, 'access-interfaces.0.tx-packets'), filter_dict(data_acc_int, 'access-interfaces.0.rx-packets')]], columns=(["access_tx_packets", "access_rx_packets"]))
                                eval(f'acc_int_chart_{i}.add_rows(add_acc_df)')

                                add_pktloss_df = pd.DataFrame([[filter_dict(data_nw_int, 'network-interfaces.0.rx-loss-packets-streams'), filter_dict(data_acc_int, 'access-interfaces.0.rx-loss-packets-streams')]], columns=(["network_interface_pkt_loss", "access_interface_pkt_loss"]))
                                eval(f'pktloss_chart_{i}.add_rows(add_pktloss_df)')

################################ Start PAGE #############################################
if st.session_state.p1:
    col30,col31,col33= st.columns([2,3,2])
    with st.container(border= True):
        with col31:
            with st.container(border= True):
                st.write(f":oil_drum: :orange[*PROVIDE YOUR BNG-BLASTER INFO*]")
                st.session_state.ip_blaster = st.selectbox(':green[IP_BLASTER] ',dict_blaster_db_format.keys(), placeholder = 'Typing your IP')
                st.session_state.port_blaster = st.text_input(':green[PORT_BLASTER] ',8001, placeholder = 'Typing your PORT')
                if dict_user_db[st.session_state.user] == 'admin1' or dict_user_db[st.session_state.user] == 'admin':
                    with st.expander(':blue[ADD NEW BNG-BLASTER CONTROLLER]'):
                        blaster_new_ip = st.text_input(':green[NEW BLASTER IP] ', placeholder = 'Typing your IP')
                        blaster_new_port = st.text_input(':green[NEW BLASTER PORT] ',8001, placeholder = 'Typing your PORT')
                        blaster_new_user = st.text_input(':green[NEW BLASTER USERNAME] ', placeholder = 'Typing your USERNAME')
                        blaster_new_passwd = st.text_input(':green[NEW BLASTER PASSWORD] ', placeholder = 'Typing your PASSWORD', type='password')
                        if st.button(":orange[**ADD NEW BLASTER**]"):
                            conn = sqlite_connect_to_db(db_name)
                            # sqlite_insert_user(conn, user, user_class)
                            sqlite_insert_blaster(conn, blaster_new_ip, blaster_new_port, blaster_new_user, blaster_new_passwd)
                            conn.close()
                            st.info(":green[Add successfully]")
            log_authorize(st.session_state.user, f'Select BNG-Blaster {st.session_state.ip_blaster}')
################################ LIST ALL INSTANCES (RUNNING +STOP) SERVER #############
blaster_server = {
    'ip': st.session_state.ip_blaster,
    'port': st.session_state.port_blaster,
}
list_instance_running_from_blaster=[]
list_instance_avail_from_blaster=[]
error = False
try:
    list_all_instances_sc, list_all_instances_ct = GET_ALL_INTANCES_BLASTER(blaster_server['ip'], blaster_server['port'])
    list_all_instances =list(json.loads(list_all_instances_ct))
    if list_all_instances_sc == 200:
        for i in list_all_instances:
            instance_exist_st, instance_exist_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], i, 'GET', payload_start)
            if "started" in str(instance_exist_ct):
                list_instance_running_from_blaster.append(i)
            else:
                list_instance_avail_from_blaster.append(i)
        for j in list_instance_avail_from_blaster:
            if j == "uploads":
                list_instance_avail_from_blaster.pop(list_instance_avail_from_blaster.index("uploads"))
        log_authorize(st.session_state.user, f'Success get BNG-Blaster_{st.session_state.ip_blaster} info')
    else:
        st.error('Can not get list-instance from server', icon="🚨")
except Exception as e:
    e1,e2,e3= st.columns([1,2,1])
    with e2:
        st.error(f"Can't get info from your BNG-Blaster server. Choose other Server available", icon="🚨")
        log_authorize(st.session_state.user, f'Fail get BNG-Blaster_{st.session_state.ip_blaster} info')
        print(f"Check your bng-blaster server.Error **{e}**")
        error = True
if st.session_state.p1:
    with col31:
        if st.button("**SELECT**", type= 'primary'):
            if error:
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= True, False, False, False, False
                st.rerun()
            else: 
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
                st.rerun()
#########################################################################################
if st.session_state.p2:
    gif1, gif2, gif3, gif4, gif5, gif6, gif7 = st.columns([0.1,2.1,0.1,1.5,0.1,2.1,0.1])
    with gif2:
        with st.container(border= True):
            gif('./images/one.gif')
            if st.button(':beginner: **PRE-RUN**', use_container_width=True):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                log_authorize(st.session_state.user, 'Select PRE-RUN page')
                st.rerun()
    with gif4:
        with st.container(border= True):
            gif('./images/two.gif')
            if st.button(':infinity:  **RUN**', use_container_width=True):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
                log_authorize(st.session_state.user, 'Select RUN page')
                st.rerun()
    with gif6:
        with st.container(border= True):
            gif('./images/three.gif')
            # if st.button(':chart_with_upwards_trend:  **REPORT**', disabled= True, use_container_width=True):
            if st.button(':chart_with_upwards_trend:  **REPORT**', use_container_width=True):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, False, True
                log_authorize(st.session_state.user, 'Select REPORT page')
                st.rerun()
if st.session_state.p3:
    st.session_state.create_instance = True
    st.title(':beginner: :rainbow[ DEFINE FILE CONFIG.JSON]')
    col51, col52 ,col53 =st.columns([19,0.9,0.9])
    with col52:
        if st.button(':house:', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
            log_authorize(st.session_state.user, 'Return HOME')
            st.rerun()
    with col53:
        if st.button(':infinity: ', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
            log_authorize(st.session_state.user, 'Change RUN page')
            st.rerun()
    tab1, tab2, tab3 = st.tabs([":bookmark_tabs: CREATE", ":pencil: MODIFY", ":inbox_tray: TEMPLATE"])
    with tab1:
        with st.container(border= True):
            st.subheader(':sunny: :green[**CREATE YOUR CONFIG**]')
            st.write(':violet[**YOUR INSTANCE NAME**]')
            with st.container(border=True):
                instance_name = st.text_input(':orange[Name of your instance] ', placeholder = 'Typing your instance name')
                if instance_name:
                    if instance_name + '.json' not in list_json:
                        st.info(':blue[Your instance\'s name can be use]', icon="🔥")
                        st.session_state.create_instance= False
                    else:
                        st.error('Your instance was duplicate, choose other name', icon="🚨")
                else:
                    st.error('Instance name can not null', icon="🔥")
            st.write(':violet[**SELECT YOUR PROTOCOLS TEMPLATES**]')
            col21, col22 = st.columns([4.2,1])
            with col21:
                with st.container(border= True):
                    select_template= st.selectbox(':orange[Select your template]?', list_templates, placeholder = 'Select one template')
            with col22:
                with st.popover(":blue[🗺️**VIEW**]", use_container_width=True):
                    st.info(":violet[Content of **%s template**]"%select_template, icon="🔥")
                    with open('%s/%s'%(path_templates,select_template), 'r') as file_template:
                        data= file_template.read()
                    st.code(data)
            col23, col24 = st.columns([2,1])
            with col23:
                with st.container(border= True):
                    st.write(':violet[**FILL YOUR VARIABLES BELOW**]')
                    list_var = get_variables_jinja_file(f'{path_templates}/{select_template}')
                    list_var.sort()
                    dict_input={}
                    index=int(len(list_var)/3)
                    col1, col2, col3 = st.columns([1,1,1])
                    with col1:
                        with st.container(border= True):
                            for i in list_var[0:index+1]:
                                exec(f"""dict_input['{i}'] = st.text_input(f':orange[**{i}**] ', placeholder = f'Typing {i}')""")
                                # st.warning('%s is null, fill it'%i, icon="🚨")
                    with col2:
                        with st.container(border= True):
                            for i in list_var[index+1:2*index+1]:
                                exec(f"""dict_input['{i}'] = st.text_input(f':orange[**{i}**] ', placeholder = f'Typing {i}')""")
                                # st.warning('%s is null, fill it'%i, icon="🚨")
                    with col3:
                        with st.container(border= True):
                            for i in list_var[2*index+1:len(list_var)]:
                                exec(f"""dict_input['{i}'] = st.text_input(f':orange[**{i}**] ', placeholder = f'Typing {i}')""")
                                # st.warning('%s is null, fill it'%i, icon="🚨")
                    # st.divider()
                    dict_check = {}
                    for d in list_var:
                        if d.endswith("address") or d.endswith("gateway") or d.endswith("gate"):
                            if is_valid_ip(dict_input[d]):
                                continue
                            else:
                                dict_check[d]= False
            with st.container(border= True):
                st.write(':violet[**INTERFACES ENABLE**]')
                str_interfaces_pre=""
                list_interfaces_templates = list(dict_interfaces_templates.keys())
                index_list_interfaces_templates = int(len(list_interfaces_templates)/2)
                col1, col2 = st.columns([1,1])
                with col1:
                    for s in list_interfaces_templates[0:index_list_interfaces_templates+1]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_interfaces}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            if var.endswith('interface'):
                                                with st.container(border= True):
                                                    st.write(f":orange[{s}/{i}/**{var}**]")
                                                    with st.container(border= True):
                                                        col_int1, col_int2 = st.columns([1.2,1])
                                                        with col_int1:
                                                            interface = st.selectbox(f":green[interface]", find_interface(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd']), key = f"{s}/{var}/{i}/interface" )
                                                        with col_int2:
                                                            vlan = st.text_input(f":green[vlan]", key=f"{s}/{var}/{i}/vlan")
                                                if vlan == "":
                                                    exec(f"""{s}_content['{var}']= interface """)
                                                else:
                                                    exec(f"""{s}_content['{var}']= interface +'.'+ vlan""")
                                            else:
                                                with st.container(border= True):
                                                    exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_interfaces}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        if i==0:
                                            str_interfaces_pre += "\n" + content
                                        else:
                                            content1 = "\n".join(content.split("\n")[1:])
                                            str_interfaces_pre += "\n" + content1
                with col2:
                    for s in list_interfaces_templates[index_list_interfaces_templates+1:len(list_interfaces_templates)]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_interfaces}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            if var.endswith('interface'):
                                                with st.container(border= True):
                                                    st.write(f":orange[{s}/{i}/**{var}**]")
                                                    with st.container(border= True):
                                                        col_int1, col_int2 = st.columns([1.2,1])
                                                        with col_int1:
                                                            interface = st.selectbox(f":green[interface]", find_interface(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd']), key =f"{s}/{var}/{i}/interface" )
                                                        with col_int2:
                                                            vlan = st.text_input(f":green[vlan]", key=f"{s}/{var}/{i}/vlan")
                                                if vlan == "":
                                                    exec(f"""{s}_content['{var}']= interface """)
                                                else:
                                                    exec(f"""{s}_content['{var}']= interface +'.'+ vlan""")
                                            else:
                                                with st.container(border= True):
                                                    exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_interfaces}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        if i==0:
                                            str_interfaces_pre += "\n" + content
                                        else:
                                            content1 = "\n".join(content.split("\n")[1:])
                                            str_interfaces_pre += "\n" + content1
            str_interfaces_pre1 = "\n  ".join(str_interfaces_pre.split("\n")[0:])
            str_interfaces = "interfaces:"+ str_interfaces_pre1
            # st.code(str_interfaces)
            with st.container(border= True):
                st.write(':violet[**STREAMS ENABLE**]')
                str_streams_pre=""
                list_streams_templates = list(dict_streams_templates.keys())
                index_list_streams_templates = int(len(list_streams_templates)/2)
                col1, col2 = st.columns([1,1])
                with col1:
                    for s in list_streams_templates[0:index_list_streams_templates+1]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_streams}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/stream_{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_streams}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        str_streams_pre += "\n" + content
                with col2:
                    for s in list_streams_templates[index_list_streams_templates+1:len(list_streams_templates)]:
                        with st.container(border= True):
                            exec(f"{s}_cb = st.checkbox(':orange[**{s}**]')")
                            if eval(f"{s}_cb"):
                                exec(f"num_{s} = st.number_input(':orange[*Number {s}*]', value=1)")
                                for i in eval(f"range(num_{s})"):
                                    with st.popover(f":blue[{s}_{i}]", use_container_width=True):
                                        exec(f"list_var_{i} = get_variables_jinja_file(f'{path_templates_streams}/{s}.j2')")
                                        exec(f"{s}_content = dict()")
                                        for var in eval(f"list_var_{i}"):
                                            exec(f"""{s}_content['{var}'] = st.text_input(f":orange[{s}/stream_{i}/**{var}**]")""")
                                        environment = Environment(loader=FileSystemLoader(f"{path_templates_streams}"))
                                        template = environment.get_template(f"{s}.j2")
                                        content= template.render(eval(f"{s}_content"))
                                        str_streams_pre += "\n" + content
            str_streams = "streams:"+ str_streams_pre     
            with col24:
                with st.container(border= True):
                    st.write(':violet[**OR IMPORT YOUR VARIABLES WITH YAML FORMAT**]')
                    dict_export_file={}
                    with st.container(border= True):
                        data_import = st.file_uploader(":orange[CHOOSE YOUR YAML FILE]", accept_multiple_files=False, disabled= st.session_state.create_instance)
                        if data_import:
                            # if data_import.name[-4:] == '.yml' or data_import.name[-5:] == '.yaml':
                            stringio = StringIO(data_import.getvalue().decode("utf-8"))
                            string_data = stringio.read()
                            try:
                                convert_yaml = yaml.load(string_data, Loader=yaml.FullLoader)
                            except Exception as e:
                                st.error(f"Can not read yaml content, check error {e}")
                            # st.write(list(convert_yaml.keys())[0])
                            if list(convert_yaml.keys())[0] == instance_name: 
                                dict_input = convert_yaml.get(instance_name)
                                # st.write(import_dict_input)
                                if '' not in dict_input.values():
                                    if set(list_var).issubset(set(list(dict_input.keys()))):
                                        # Pop items no need
                                        pop=[]
                                        for e in list(dict_input.keys()):
                                            if e not in list_var:
                                                pop.append(e)
                                        for i in range(len(pop)):
                                            dict_input.pop(pop[i])
                                        dict_input['template']= select_template # Save mapping config: template
                                        st.info(':blue[Import variables successfully]', icon="🔥")
                                        log_authorize(st.session_state.user, 'IMPORT yaml file')
                                    else:
                                        list_var_lack= set(list_var).difference(set(list(dict_input.keys())))
                                        st.error(f'Data lack of vars **{list_var_lack}**', icon="🚨")
                                else:
                                    st.error('Have values empty', icon="🚨")
                            else:
                                st.error('Could not change intance-name', icon="🚨")
                            # else:
                            #     st.error('Upload file with .yaml or .yml , please. No accept other types ', icon="🚨")
                    if instance_name:
                        dict_export_file[instance_name] = dict_input
                        st.download_button(':green[DATA_FORMAT]', '---\n'+yaml.dump(dict_export_file, indent = 2, encoding= None), disabled= st.session_state.create_instance)
            with st.popover(":blue[**REVIEW**]", use_container_width=True):
                environment = Environment(loader=FileSystemLoader(f"{path_templates}"))
                template = environment.get_template(f"{select_template}")
                if str_streams== "streams:":
                    if str_interfaces =="interfaces:":
                        review_content= template.render(dict_input)
                    else:
                        review_content= template.render(dict_input) + '\n' + str_interfaces
                else:
                    if str_interfaces =="interfaces:":
                        review_content= template.render(dict_input) + '\n' + str_streams
                    else:
                        review_content= template.render(dict_input) + '\n' + str_interfaces + '\n' + str_streams
                    # review_content= template.render(dict_input) + '\n' + str_streams
                st.code(review_content)
            if st.button('**CREATE INSTANCE**', type= 'primary', disabled = st.session_state.create_instance):
                st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4,st.session_state.p5= False,False, True, False, False
                # if "" not in dict_input.values():
                if len(list(dict_check.keys())) == 0:
                    environment = Environment(loader=FileSystemLoader(f"{path_templates}"))
                    template = environment.get_template(f"{select_template}")
                    if str_streams== "streams:":
                        if str_interfaces =="interfaces:":
                            content= template.render(dict_input)
                        else:
                            content= template.render(dict_input) + '\n' + str_interfaces
                    else:
                        if str_interfaces =="interfaces:":
                            content= template.render(dict_input) + '\n' + str_streams
                        else:
                            content= template.render(dict_input) + '\n' + str_interfaces + '\n' + str_streams
                    with open('%s/%s.json'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as config:
                        # config.write(content)
                        json.dump(yaml.safe_load(content), config, indent=2)
                    dict_data, dict_data_input={}, {} # Build dict of data
                    for i in dict_input.keys():
                        dict_data_input.update({i: dict_input[i]})
                    dict_data_input['template']= select_template # Save mapping config: template
                    dict_data[instance_name]= dict_data_input
                    with open('%s/%s.yml'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as file_data:
                        file_data.write('---\n')
                        file_data.write(yaml.dump(dict_data))
                        file_data.write('\n')
                    if str_streams != "streams:":
                        with open('%s/%s_streams.yml'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as file_data_streams:
                            file_data_streams.write('---\n')
                            file_data_streams.write(str_streams)
                    if str_interfaces != "interfaces:":
                        with open('%s/%s_interfaces.yml'%(path_configs,instance_name), mode= 'w', encoding= 'utf-8') as file_data_interfaces:
                            file_data_interfaces.write('---\n')
                            file_data_interfaces.write(str_interfaces)
                    st.info(':blue[Create successfully]', icon="🔥")
                    log_authorize(st.session_state.user, f'CREATE intance {instance_name}')
                    time.sleep(3)
                    st.rerun()
                else:
                    for i in dict_check.keys():
                        st.error(f'Input **{i}** wrong, check IP format before create, please', icon="🚨")    
    with tab2:
        with st.container(border= True):
            st.subheader(':sunny: :green[**MODIFY YOUR CONFIG**]')
            st.write(':violet[**YOUR INSTANCE NAME**]')
            st.session_state.edit_instance= False
            edit_list_var=[]
            with st.container(border=True):
                edit_instance= st.selectbox(':orange[Select your instance for modifing]?', list_instance, placeholder = 'Select one instance')
            try:
                with open("%s/%s.yml"%(path_configs,edit_instance) , 'r') as file_data:
                    config_data = yaml.load(file_data, Loader=yaml.FullLoader)
                    edit_template= config_data[edit_instance]['template']
                    edit_list_var = get_variables_jinja_file(f'{path_templates}/{edit_template}')
                    edit_list_var.sort()
            except Exception as ex:
                st.error(f"Can not load data file {ex}")
            edit_dict_input={}
            if edit_list_var:
                st.write(':violet[**EDIT YOUR PROTOCOLS VARIABLE BELOW**]')
                index=int(len(edit_list_var)/3)
                with st.container(border= True):
                    col1, col2, col3 = st.columns([1,1,1])
                    with col1:
                        with st.container(border= True):
                            for i in edit_list_var[0:index+1]:
                                exec(f"""edit_dict_input['{i}'] = st.text_input(f':orange[Modify **{i}**] ',config_data['{edit_instance}']['{i}'], placeholder = f'Typing {i}')""")
                    with col2:
                        with st.container(border= True):
                            for i in edit_list_var[index+1:2*index+1]:
                                exec(f"""edit_dict_input['{i}'] = st.text_input(f':orange[Modify **{i}**] ',config_data['{edit_instance}']['{i}'], placeholder = f'Typing {i}')""")
                    with col3:
                        with st.container(border= True):
                            for i in edit_list_var[2*index+1:len(edit_list_var)]:
                                exec(f"""edit_dict_input['{i}'] = st.text_input(f':orange[Modify **{i}**] ',config_data['{edit_instance}']['{i}'], placeholder = f'Typing {i}')""") 
            else:
                print('Can not load jinja template')
            if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                with open('%s/%s_interfaces.yml'%(path_configs,edit_instance), mode= 'r') as interfaces:
                    edit_interfaces_input= yaml.safe_load(interfaces.read())
                edit_list_key_interfaces = list(edit_interfaces_input['interfaces'].keys())
                if len(edit_interfaces_input['interfaces']) == 0 :
                    st.write("interfaces null")
                else:
                    dict_edit_interfaces ={}
                    st.write(f':violet[**EDIT INTERFACES VARIABLE BELOW**]')
                    with st.container(border= True):
                        index_int = int(len(edit_list_key_interfaces)/2)
                        col1, col2= st.columns([1,1])
                        with col1:
                            for key in edit_list_key_interfaces[0:index_int+1]:
                                exec(f"edit_interfaces_{key} = []")
                                with st.container(border= True):
                                    st.write(f':green[**interfaces/{key}**]')
                                    for i in range(len(edit_interfaces_input['interfaces'][key])):
                                        temp_edit_interfaces ={}
                                        with st.popover(f":orange[interfaces_{key}_{i}]", use_container_width=True):
                                            list_input= edit_interfaces_input['interfaces'][key][i].keys()
                                            for j in list_input:
                                                exec(f"""temp_edit_interfaces['{j}'] = st.text_input(f":orange[interaces_{key}_{i}]/:orange[**{j}**]", edit_interfaces_input['interfaces'][key][i]['{j}'])""")
                                        eval(f"edit_interfaces_{key}.append(temp_edit_interfaces)")
                                        if i == (len(edit_interfaces_input['interfaces'][key])-1):
                                            exec(f"dict_edit_interfaces[key] = edit_interfaces_{key}")
                                        
                                    ###### Convert value of interface value to int #############################
                                    for i in eval(f"edit_interfaces_{key}"):
                                        list_keys = list(i.keys())
                                        for j in list_keys:
                                            try:
                                                temp=int(i[j])
                                                i[j] = temp
                                            except:
                                                continue
                        with col2:
                            for key in edit_list_key_interfaces[index_int+1:len(edit_list_key_interfaces)]:
                                exec(f"edit_interfaces_{key} = []")
                                with st.container(border= True):
                                    st.write(f':green[**interfaces/{key}**]')
                                    for i in range(len(edit_interfaces_input['interfaces'][key])):
                                        temp_edit_interfaces ={}
                                        with st.popover(f":orange[interfaces_{key}_{i}]", use_container_width=True):
                                            list_input= edit_interfaces_input['interfaces'][key][i].keys()
                                            for j in list_input:
                                                exec(f"""temp_edit_interfaces['{j}'] = st.text_input(f":orange[interaces_{key}_{i}]/:orange[**{j}**]", edit_interfaces_input['interfaces'][key][i]['{j}'])""")
                                        eval(f"edit_interfaces_{key}.append(temp_edit_interfaces)")
                                        if i == (len(edit_interfaces_input['interfaces'][key])-1):
                                            exec(f"dict_edit_interfaces[key] = edit_interfaces_{key}")
                                    ###### Convert value of interface value to int #############################
                                    for i in eval(f"edit_interfaces_{key}"):
                                        list_keys = list(i.keys())
                                        for j in list_keys:
                                            try:
                                                temp=int(i[j])
                                                i[j] = temp
                                            except:
                                                continue
                        # st.write(dict_edit_interfaces)
            if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                # st.divider()
                with open('%s/%s_streams.yml'%(path_configs,edit_instance), mode= 'r') as streams:
                    edit_streams_input= yaml.safe_load(streams.read())
                # st.write(edit_streams_input['streams'])
                if len(edit_streams_input['streams']) == 0 :
                    st.write("streams null")
                else:
                    edit_streams = []
                    st.write(':violet[**EDIT STREAMS VARIABLE BELOW**]')
                    with st.container(border= True):
                        index_col = int(len(edit_streams_input['streams'])/2)
                        col1, col2= st.columns([1,1])
                        with col1:
                            for i in range(0,index_col+1):
                                temp_edit_streams ={}
                                with st.popover(f":orange[stream_{i}]", use_container_width=True):
                                    list_input= edit_streams_input['streams'][i].keys()
                                    for j in list_input:
                                        exec(f"""temp_edit_streams['{j}'] = st.text_input(f":orange[streams_{i}]/:orange[**{j}**]", edit_streams_input['streams'][i]['{j}'])""")
                                edit_streams.append(temp_edit_streams)
                        with col2:
                            for i in range(index_col+1,len(edit_streams_input['streams'])):
                                temp_edit_streams ={}
                                with st.popover(f":orange[stream_{i}]", use_container_width=True):
                                    list_input= edit_streams_input['streams'][i].keys()
                                    for j in list_input:
                                        exec(f"""temp_edit_streams['{j}'] = st.text_input(f":orange[streams_{i}]/:orange[**{j}**]", edit_streams_input['streams'][i]['{j}'])""")
                                edit_streams.append(temp_edit_streams)
                ###### Convert value of streams to int #############################
                for i in edit_streams:
                    list_keys = list(i.keys())
                    for j in list_keys:
                        try:
                            temp=int(i[j])
                            i[j] = temp
                        except:
                            continue
                # st.write(edit_streams)
            st.divider()
            edit_content=""
            col14, col15, col16 = st.columns([1,4,1])
            with col14:
                if st.button('**SAVE**', type= 'primary', disabled = st.session_state.edit_instance, use_container_width=True):
                    st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False,False, True, False, False
                    if "" not in edit_dict_input.values():
                        streams_save={}
                        interfaces_save={}
                        if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                            streams_save['streams']= edit_streams
                        if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                            interfaces_save['interfaces']= dict_edit_interfaces
                        # Render config from Jinja file
                        environment = Environment(loader=FileSystemLoader(f"{path_templates}"))
                        template = environment.get_template(f"{config_data[edit_instance]['template']}")
                        edit_content = template.render(edit_dict_input)
                        ### Save new config
                        with open('%s/%s.json'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as edit_config:
                            if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                                if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                                    edit_content += "\n" + yaml.dump(streams_save) + "\n" +yaml.dump(interfaces_save)
                                else:
                                    edit_content += "\n" + yaml.dump(streams_save)
                            else:
                                if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                                    edit_content += "\n" +yaml.dump(interfaces_save)
                            json.dump(yaml.safe_load(edit_content), edit_config, indent=2)
                        save_dict_data, save_dict_data_input={}, {} # Build dict of data
                        for i in edit_dict_input.keys():
                            save_dict_data_input.update({i: edit_dict_input[i]})
                        save_dict_data_input['template']= config_data[edit_instance]['template'] # Save mapping config: template
                        save_dict_data[edit_instance]= save_dict_data_input
                        ### Save data instance to yaml
                        with open('%s/%s.yml'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as data:
                            data.write('---\n')
                            data.write(yaml.dump(save_dict_data))
                            data.write('\n')
                        ### Save interfaces to yaml
                        if os.path.exists('%s/%s_interfaces.yml'%(path_configs,edit_instance)):
                            with open('%s/%s_interfaces.yml'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as interfaces_data:
                                interfaces_data.write('---\n')
                                interfaces_data.write(yaml.dump(interfaces_save))
                        ### Save streams to yaml
                        if os.path.exists('%s/%s_streams.yml'%(path_configs,edit_instance)):
                            with open('%s/%s_streams.yml'%(path_configs,edit_instance), mode= 'w', encoding= 'utf-8') as streams_data:
                                streams_data.write('---\n')
                                streams_data.write(yaml.dump(streams_save))
                        st.toast(':blue[Save instance %s successfully]'%edit_instance, icon="🔥")
                        log_authorize(st.session_state.user, f'Edit and save instance {edit_instance}')
                    else:
                        st.toast(':red[Have parameters empty, fill us before save, please]', icon="🚨")
            with col16:
                if st.button('**DELETE**', use_container_width=True):
                    st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                    delete_config(path_configs, edit_instance)
            if edit_content != "":
                with st.popover(":green[**REVIEW**]", use_container_width=True):
                    # st.json(yaml.safe_load(edit_content))
                    st.code(edit_content)
    if dict_user_db[st.session_state.user] == 'admin' or dict_user_db[st.session_state.user] == 'admin1':
        with tab3:
            with st.container(border= True):
                st.subheader(':sunny: :green[YOUR SELECTION]')
                import_radio = st.radio(
                    ":violet[SELECT KIND OF TEMPLATES BELOW]",
                    [":orange[PROTOCOLS]", ":orange[INTERFACES]", ":orange[STREAMS]"],
                    index=None,
                )
            if import_radio == ":orange[PROTOCOLS]":
                col1_template, col2_template = st.columns([1.25,1])
                with col2_template:
                    with st.container(border=True, height=630):
                        st.subheader(':desktop_computer: :green[IMPORT PROTOCOLS TEMPLATE]')
                        st.write(':violet[Upload protocols template]')
                        protocols_file_import = st.file_uploader("Choose a Template file", accept_multiple_files=False)
                        if protocols_file_import:
                            if protocols_file_import.name[-3:] == '.j2':
                                stringio = StringIO(protocols_file_import.getvalue().decode("utf-8"))
                                string_data = stringio.read() 
                                if protocols_file_import.name not in list_templates:
                                    with open(f"{path_templates}/{protocols_file_import.name}", 'w') as jinja:
                                        jinja.write(string_data)
                                        st.info(':blue[Upload template %s successfully]'%protocols_file_import.name, icon="🔥")
                                        log_authorize(st.session_state.user, f'Import protocols template file {protocols_file_import.name}')
                                else:
                                    st.error('Duplicate name file, change your file name and try again', icon="🚨")
                            else:
                                st.error('Upload file with .j2 , please. No accept other types ', icon="🚨")
                        else:
                            st.info(':blue[Select file upload]', icon="🔥")
                with col1_template:
                    with st.container(border=True):
                        st.subheader(':memo: :green[EDIT PROTOCOLS TEMPLATE]')
                        template_edit = st.selectbox(':orange[Select your template for editing]?', list_templates, placeholder = 'Select one template')
                        with open(f"{path_templates}/{template_edit}", "r") as view:
                            cont1= view.read()
                        with st.container(border=True):
                            edit_template_text = st_ace(
                            value= cont1,
                            language= 'yaml', 
                            theme= '', 
                            show_gutter= True, 
                            keybinding='vscode', 
                            auto_update= True, 
                            placeholder= '*Edit your template*',
                            height=350)
                        col100, col101, col102 =st.columns([1,2,1])
                        with col100:
                            if st.button("SAVE", type = 'primary', use_container_width= True):
                                with open(f"{path_templates}/{template_edit}", "w") as write:
                                    write.write(edit_template_text)
                                st.toast(f':blue[Save your template **{template_edit}** successfully]', icon="🔥")
                        with col102:
                            if st.button("DELETE", use_container_width= True):
                                os.remove(f"{path_templates}/{template_edit}")
                                st.info(':blue[Delete successfully]', icon="🔥")
                                st.rerun()
            if import_radio == ":orange[INTERFACES]":
                col1_template, col2_template = st.columns([1.25,1])
                with col2_template:
                    with st.container(border=True, height=630):
                        st.subheader(':desktop_computer: :green[IMPORT INTERFACES TEMPLATE]')
                        st.write(':violet[Upload interfaces template]')
                        protocols_file_import = st.file_uploader("Choose a Template file", accept_multiple_files=False)
                        if protocols_file_import:
                            if protocols_file_import.name[-3:] == '.j2':
                                stringio = StringIO(protocols_file_import.getvalue().decode("utf-8"))
                                string_data = stringio.read() 
                                if protocols_file_import.name not in list_templates:
                                    with open(f"{path_templates_interfaces}/{protocols_file_import.name}", 'w') as jinja:
                                        jinja.write(string_data)
                                        st.info(':blue[Upload template %s successfully]'%protocols_file_import.name, icon="🔥")
                                        log_authorize(st.session_state.user, f'Import interfaces template file {protocols_file_import.name}')
                                else:
                                    st.error('Duplicate name file, change your file name and try again', icon="🚨")
                            else:
                                st.error('Upload file with .j2 , please. No accept other types ', icon="🚨")
                        else:
                            st.info(':blue[Select file upload]', icon="🔥")
                with col1_template:
                    with st.container(border=True):
                        st.subheader(':memo: :green[EDIT INTERFACES TEMPLATE]')
                        template_edit = st.selectbox(':orange[Select your template for editing]?', list_interfaces, placeholder = 'Select one template')
                        with open(f"{path_templates_interfaces}/{template_edit}.j2", "r") as view:
                            cont1= view.read()
                        with st.container(border=True):
                            edit_template_text = st_ace(
                            value= cont1,
                            language= 'yaml', 
                            theme= '', 
                            show_gutter= True, 
                            keybinding='vscode', 
                            auto_update= True, 
                            placeholder= '*Edit your template*',
                            height=350)
                        col100, col101, col102 =st.columns([1,2,1])
                        with col100:
                            if st.button("SAVE", type = 'primary', use_container_width= True):
                                with open(f"{path_templates_interfaces}/{template_edit}.j2", "w") as write:
                                    write.write(edit_template_text)
                                st.toast(f':blue[Save your template **{template_edit}** successfully]', icon="🔥")
                        with col102:
                            if st.button("DELETE", use_container_width= True):
                                os.remove(f"{path_templates_interfaces}/{template_edit}.j2")
                                st.info(':blue[Delete successfully]', icon="🔥")
                                st.rerun()
            if import_radio == ":orange[STREAMS]":
                col1_template, col2_template = st.columns([1.25,1])
                with col2_template:
                    with st.container(border=True, height=630):
                        st.subheader(':desktop_computer: :green[IMPORT STREAMS TEMPLATE]')
                        st.write(':violet[Upload streams template]')
                        streams_file_import = st.file_uploader("Choose a Template file", accept_multiple_files=False)
                        if streams_file_import:
                            if streams_file_import.name[-3:] == '.j2':
                                stringio = StringIO(streams_file_import.getvalue().decode("utf-8"))
                                string_data = stringio.read() 
                                if streams_file_import.name not in list_templates:
                                    with open(f"{path_templates_streams}/{streams_file_import.name}", 'w') as jinja:
                                        jinja.write(string_data)
                                        st.info(':blue[Upload template %s successfully]'%streams_file_import.name, icon="🔥")
                                        log_authorize(st.session_state.user, f'Import template file {streams_file_import.name}')
                                else:
                                    st.error('Duplicate name file, change your file name and try again', icon="🚨")
                            else:
                                st.error('Upload file with .j2 , please. No accept other types ', icon="🚨")
                        else:
                            st.info(':blue[Select file upload]', icon="🔥")
                with col1_template:
                    with st.container(border=True):
                        st.subheader(':memo: :green[EDIT STREAMS TEMPLATE]')
                        template_edit = st.selectbox(':orange[Select your template for editing]?', list_streams_templates, placeholder = 'Select one template')
                        with open(f"{path_templates_streams}/{template_edit}.j2", "r") as view:
                            cont1= view.read()
                        with st.container(border=True):
                            edit_template_text = st_ace(
                            value= cont1,
                            language= 'yaml', 
                            theme= '', 
                            show_gutter= True, 
                            keybinding='vscode', 
                            auto_update= True, 
                            placeholder= '*Edit your template*',
                            height=350)
                        col100, col101, col102 =st.columns([1,2,1])
                        with col100:
                            if st.button("SAVE", use_container_width=True, type = 'primary'):
                                with open(f"{path_templates_streams}/{template_edit}.j2", "w") as write:
                                    write.write(edit_template_text)
                                st.toast(f':blue[Save your template **{template_edit}** successfully]', icon="🔥")
                        with col102:
                            if st.button("DELETE", use_container_width= True):
                                os.remove(f"{path_templates_streams}/{template_edit}.j2")
                                st.info(':blue[Delete successfully]', icon="🔥")
                                st.rerun()
            if import_radio == ":orange[PROTOCOLS]":
                with st.container(border= True):
                    st.subheader(':package: :green[BUILD YOUR PROTOCOLS TEMPLATE]')
                    # st.write(list_part)
                    output_str=""
                    st.write(":violet[Select your pieces of your template]")
                    with st.container(border=True):
                        col1_temp, col2_temp = st.columns([1,1])
                        index_temp = int(len(list_part)/2)
                        with col1_temp:
                            for i in list_part[0:index_temp+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_element_config[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= True, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_part.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        with col2_temp:
                            for i in list_part[index_temp+1:len(list_part)+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_element_config[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= True, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_part.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        name_template = st.text_input(':violet[Input your name of new template]')
                        if (f"{name_template}.j2") in list_templates:
                            st.error('Name existed, try other name', icon="🚨")
                            st.session_state.save_template= True
                        else:
                            if name_template == "":
                                st.warning("Name can not null", icon="🔥")
                                st.session_state.save_template= True
                            else:
                                st.info("You can use this name", icon="🔥")
                                st.session_state.save_template= False
                    if st.button("**SAVE**", type= 'primary', disabled= st.session_state.save_template):
                        if output_str != "":
                            with open(f"{path_templates}/{name_template}.j2", 'w') as file:
                                file.write(output_str)
                            st.code(output_str)
                        else:
                            st.error("Select above first", icon="🚨")
            if import_radio == ":orange[INTERFACES]":
                with st.container(border= True):
                    st.subheader(':package: :green[BUILD YOUR INTERFACES TEMPLATE]')
                    # st.write(list_interfaces)
                    output_str=""
                    st.write(":violet[Select your pieces of your template]")
                    with st.container(border=True):
                        col1_temp, col2_temp = st.columns([1,1])
                        index_temp = int(len(list_interfaces)/2)
                        with col1_temp:
                            for i in list_interfaces[0:index_temp+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]', key='{i}')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_interfaces_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= True, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_interfaces.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        with col2_temp:
                            for i in list_interfaces[index_temp+1:len(list_interfaces)+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[**{i}**]', key='{i}')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_interfaces_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= True, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_interfaces.index(i))
                                            #########################################
                                            output_str += '\n' + add_part
                        name_template = st.text_input(':violet[Input your name of new template]')
                        if (f"{name_template}") in list_interfaces:
                            st.error('Name existed, try other name', icon="🚨")
                            st.session_state.save_template= True
                        else:
                            if name_template == "":
                                st.warning("Name can not null", icon="🔥")
                                st.session_state.save_template= True
                            else:
                                st.info("You can use this name", icon="🔥")
                                st.session_state.save_template= False
                    if st.button("**SAVE**", type= 'primary', disabled= st.session_state.save_template):
                        if output_str != "":
                            with open(f"{path_templates_interfaces}/{name_template}.j2", 'w') as file:
                                file.write(output_str)
                            st.code(output_str)
                        else:
                            st.error("Select above first", icon="🚨")
            if import_radio == ":orange[STREAMS]":
                with st.container(border= True):
                    st.subheader(':package: :green[BUILD YOUR STREAMS TEMPLATE]')
                    # st.write(list_part)
                    streams_output_str=""
                    st.write(":violet[Select your pieces of your template]")
                    with st.container(border=True):
                        col1_temp, col2_temp = st.columns([1,1])
                        index_temp = int(len(list_streams)/2)
                        with col1_temp:
                            for i in list_streams[0:index_temp+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[.**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_streams_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= True, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_streams.index(i))
                                            #########################################
                                            streams_output_str += '\n' + add_part
                        with col2_temp:
                            for i in list_streams[index_temp+1:len(list_streams)+1]:
                                with st.container(border=True):
                                    if eval(f"st.checkbox(':orange[.**{i}**]')"):
                                        with eval(f"st.expander(':green[Edit **{i}** pieces]')"):
                                            add_part= st_ace(
                                            value= dict_streams_templates[i],
                                            language= 'yaml', 
                                            theme= '', 
                                            show_gutter= True, 
                                            keybinding='vscode', 
                                            auto_update= True, 
                                            placeholder= '*Edit your template*', 
                                            height= 300,
                                            key= list_streams.index(i))
                                            #########################################
                                            streams_output_str += '\n' + add_part
                        name_template = st.text_input(':violet[Input your name of new template]',"streams_")
                        if (f"{name_template}.j2") in list_streams:
                            st.error('Name existed, try other name', icon="🚨")
                            st.session_state.save_template= True
                        else:
                            if name_template == "streams_":
                                st.warning("Typing your name", icon="🔥")
                                st.session_state.save_template= True
                            else:
                                st.info("You can use this name", icon="🔥")
                                st.session_state.save_template= False
                    if st.button("**SAVE**", type= 'primary', disabled= st.session_state.save_template):
                        if streams_output_str != "":
                            with open(f"{path_templates_streams}/{name_template}.j2", 'w') as file:
                                file.write(streams_output_str)
                            st.code(streams_output_str)
                        else:
                            st.error("Select above first", icon="🚨")
if st.session_state.p4:
    st.title(':infinity: :rainbow[RUN BLASTER]')
    col41, col42 ,col43 =st.columns([19,0.9,0.9])
    with col42:
        if st.button(':house:', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
            st.rerun()
    with col43:
        if st.button(":chart_with_upwards_trend: ", use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, False, True
            st.rerun()
    blaster_status(blaster_server['ip'],blaster_server['port'],list_instance_running_from_blaster, list_instance_avail_from_blaster) # call function display status of blaster server
    col4, col5=st.columns([1.5,1])
    with col4:
        with st.container(border= True):
            st.subheader(':sunny: :green[TEST MANAGEMENT]')
            col19, col20 =st.columns([2,1])
            with col19:
                with st.container(border= True):
                    instance= st.selectbox(':orange[Select your instance]?', list_instance, placeholder = 'Select one instance')
            with col20:
                with st.popover("🗺️CONFIG", use_container_width=True):
                    st.info(":violet[Content of **%s.json**]"%instance, icon="🔥")
                    with open('%s/%s.json'%(path_configs, instance), 'r') as file_show:
                        data= file_show.read()
                    st.code(data)
                    if st.button('**EDIT**', use_container_width=True):
                        st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, True, False, False
                        log_authorize(st.session_state.user, 'Change RUN to PRE-RUN for EDIT')
                        st.rerun()
            instance_exist_st, instance_exist_ct = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start)
            if "started" in str(instance_exist_ct):
                st.session_state.button_start= True
                st.session_state.button_stop= False
                with col19:
                    st.warning("This instance already running", icon="🔥")
                with open('%s/%s.yml'%(path_configs,instance), 'r') as file_temp:
                    run_template = yaml.load(file_temp, Loader=yaml.FullLoader)
                col17, col18 =st.columns([1,1])
                if run_template[instance]['template'] == "bgp.j2":
                    with col17:
                        with st.form('ADVERTISE'):
                            prefix= st.text_input(f":orange[Your prefix you want advertise: ]","", placeholder = "Fill your IP prefix")
                            num_prefix= st.text_input(f":orange[Your number of prefixs you want advertise: ]","", placeholder = "Fill number")
                            submitted = st.form_submit_button(label= "ADVERTISE")
                            if submitted:
                                if "/" in prefix and prefix:
                                    name_bgp_update = instance + "_"+ prefix.split('/')[0]+"_"+num_prefix
                                    payload_command_bgp_raw_update= """
                                    {
                                        "command": "bgp-raw-update",
                                        "arguments": {
                                            "file": "/var/bngblaster/uploads/%s.bgp"
                                        }
                                    }
                                    """%name_bgp_update
                                    if prefix and num_prefix:
                                        # subprocess.run(["bgpupdate","-f", "%s.bgp"%instance,"-a", run_template[instance]['local_as'], "-n",run_template[instance]['bgp_local_address'], "-p", prefix, "-P",num_prefix,"-f", "withdraw.bgp","--withdraw"], capture_output=True, text=True)
                                        result = subprocess.run(["bgpupdate","-f", "./bgp_update/%s.bgp"%name_bgp_update,"-a", run_template[instance]['local_as'], "-n",run_template[instance]['bgp_local_address'], "-p", prefix, "-P",num_prefix], capture_output=True, text=True)
                                        if 'error' not in str(result):
                                            # send_file = push_file_to_server_rest_api(blaster_server['ip'], '5000', './bgp_update/%s.bgp'%name_bgp_update)
                                            push_file_to_server_by_ftp(blaster_server['ip'],dict_blaster_db_format[blaster_server['ip']]['user'], dict_blaster_db_format[blaster_server['ip']]['passwd'],f"{path_bgp_update}/{name_bgp_update}.bgp", f'/var/bngblaster/uploads/{name_bgp_update}.bgp')
                                            adv_sc, adv_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_command_bgp_raw_update, '/_command')
                                            st.info(':blue[Advertise sucessfully]', icon="🔥")
                                            log_authorize(st.session_state.user, f'Advertise BGP route {prefix} num {num_prefix}')
                                        else:
                                            st.error(":violet[Wrong prefix]", icon="🔥")
                                    else:
                                        st.error(":violet[Fill prefix advertise above first]", icon="🔥")
                                else:
                                    st.error('Type your prefix with subnet mask, plz', icon="🚨")
                    with col18:
                        with st.form('WITHDRAW'):
                            prefix_wd= st.text_input(f":orange[Your prefix you want withdraw: ]","", placeholder = "Fill your IP prefix")
                            num_prefix_wd= st.text_input(f":orange[Your number of prefixs you want withdraw: ]","", placeholder = "Fill number")
                            submitted = st.form_submit_button(label= "WITHDRAW")
                            if submitted:
                                if "/" in prefix_wd and prefix_wd:
                                    name_bgp_update_wd = instance+"_withdraw_"+ prefix_wd.split('/')[0]+"_"+num_prefix_wd
                                    payload_command_bgp_raw_update_wd= """
                                    {
                                        "command": "bgp-raw-update",
                                        "arguments": {
                                            "file": "/var/bngblaster/uploads/%s.bgp"
                                        }
                                    }
                                    """%name_bgp_update_wd
                                    if prefix_wd and num_prefix_wd:
                                        result_wd= subprocess.run(["bgpupdate","-a", run_template[instance]['local_as'], "-n",run_template[instance]['bgp_local_address'], "-p", prefix_wd, "-P",num_prefix_wd,"-f", "./bgp_update/%s.bgp"%name_bgp_update_wd,"--withdraw"], capture_output=True, text=True)
                                        if "error" not in str(result_wd):
                                            # send_file_wd = push_file_to_server_rest_api(blaster_server['ip'], '5000', './bgp_update/%s.bgp'%name_bgp_update_wd)
                                            push_file_to_server_by_ftp(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']]['user'],dict_blaster_db_format[blaster_server['ip']]['passwd'] ,f"{path_bgp_update}/{name_bgp_update_wd}.bgp", f'/var/bngblaster/uploads/{name_bgp_update_wd}.bgp')
                                            wd_sc, wd_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_command_bgp_raw_update_wd, '/_command')
                                            st.info(':blue[Withdraw sucessfully]', icon="🔥")
                                            log_authorize(st.session_state.user, f'Withdraw BGP route {prefix_wd} num {num_prefix_wd}')
                                        else:
                                            st.error(":violet[Wrong prefix]", icon="🔥")
                                    else:
                                        st.error(":violet[Fill prefix withdraw above first]", icon="🔥")
                                else:
                                    st.error('Type your prefix with subnet mask, plz', icon="🚨")
            else:
                with col19:
                    st.session_state.button_start= False
                    st.session_state.button_stop= True
                    if instance in list_instance_avail_from_blaster:
                        st.warning(f'Instance **{instance}** can start but its config will be overrided', icon="🔥")
                    else:
                        st.info("You can start this instance", icon="🔥")
            with col19:
                if st.button('**START** :arrow_forward: ', type = 'primary',use_container_width=True, disabled= st.session_state.button_start):
                    # st.write('Traffic\'s running')
                    # st.code(os.popen("netstat -i").read())
                    try:
                        exist_sc, exist_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start)
                        # st.write(exist_sc, exist_ct)
                    except Exception as e:
                        st.info(f'Error {e}')
                    if exist_sc == 200:
                        st.write(':orange[Start traffic generating ...]')
                        with open(f'{path_configs}/{instance}.json') as file:
                            exist_put_body= json.load(file)
                        CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'PUT', json.dumps(exist_put_body, indent=2))
                        start_exist_sc, start_exist_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_start, '/_start')
                        #st.write(start_exist_sc, start_exist_ct)
                        run_pg1 = st.progress(0)
                        for percent_complete3 in range(100):
                            time.sleep(0.01)
                            run_pg1.progress(percent_complete3 + 1, text= f':violet[{percent_complete3+1}%]')
                    else:
                        ######## Push config.json ##############################
                        with open(f'{path_configs}/{instance}.json') as file:
                            put_body= json.load(file)
                        st.write(':orange[Put config.json ...]')
                        put_sc, put_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'PUT', json.dumps(put_body, indent=2))
                        put_pg = st.progress(0)
                        for percent_complete1 in range(100):
                            time.sleep(0.01)
                            put_pg.progress(percent_complete1 + 1, text= f':violet[{percent_complete1+1}%]')
                        ######## Start trafffic ##############################
                        st.write(':orange[Start traffic generating ...]')
                        start_sc, start_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_start, '/_start')
                        # st.write(start_sc, start_ct)
                        run_pg = st.progress(0)
                        for percent_complete2 in range(100):
                            time.sleep(0.01)
                            run_pg.progress(percent_complete2 + 1, text= f':violet[{percent_complete2+1}%]')
                        if put_sc == 201:
                            print('Create instance on blaster sucessfully')
                        else: 
                            print('Create instance on blaster didnt sucessfully')
                    st.session_state.button_stop= False
                    log_authorize(st.session_state.user, f'RUN START instance {instance}')
                    time.sleep(1)
                    st.rerun()
                # with st.container(border= True):
                if st.button('**STOP** :octagonal_sign:', type= 'primary', use_container_width=True, disabled= st.session_state.button_stop):
                    stop_sc, stop_ct= CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'POST', payload_stop, '/_stop')
                    # st.write(stop_sc, stop_ct)
                    st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
                    log_authorize(st.session_state.user, f'RUN STOP instance {instance}')
                    
                    stop_pg = st.progress(0)
                    for percent_complete3 in range(100):
                        time.sleep(0.04)
                        stop_pg.progress(percent_complete3 + 1, text= f':violet[{percent_complete3+1}%]')
                    st.info(":green[Stop successfully]", icon="🔥")
                    time.sleep(1)
                    st.rerun()
    with col5:
        with st.container(border= True):
            st.subheader(':sunny: :green[OUTPUT LOGGING]')
            if ("started" in str(instance_exist_ct)) or ("stopped" in str(instance_exist_ct)):
                run_out=''
                run_log= ''
                run_err= ''
                if instance:
                    run_log_sc, run_log = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start, '/run.log')
                    run_out_sc, run_out = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start, '/run.stdout')
                    run_err_sc, run_err = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance, 'GET', payload_start, '/run.stderr')
                if run_log != '':
                    with st.status(':violet[ALL_RUNNING_LOG]', expanded=False):
                        for i in str(run_log).split('\\n')[-50:-1]:
                            # time.sleep(0.01)
                            st.text('%s'%i)
                if run_out != '':
                    with st.status(':violet[RUNNING_LOG]', expanded=False):
                        for i in str(run_out).split('\\n')[-30:-1]:
                            # time.sleep(0.01)
                            st.text('%s'%i)            
                if run_err != '':
                    with st.status(':violet[ERROR_LOG]', expanded=False):
                        for i in str(run_err).split('\\n')[-30:-1]:
                            # time.sleep(0.01)
                            st.text('%s'%i)
if st.session_state.p5:
    st.title(':chart_with_upwards_trend: :rainbow[DASHBOARD]')
    col61, col62 ,col63 =st.columns([19,0.9,0.9])
    with col62:
        # if st.button('◀️'):
        if st.button(':house: ', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, True, False, False, False
            log_authorize(st.session_state.user, 'REPORT return HOME')
            st.rerun()
    with col63:
        if st.button(':infinity:', use_container_width=True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= False, False, False, True, False
            log_authorize(st.session_state.user, 'REPORT return RUN')
            st.rerun()
    blaster_status(blaster_server['ip'],blaster_server['port'],list_instance_running_from_blaster, list_instance_avail_from_blaster) # call function display status of blaster server
    # instance_running= ['bgp_linhnt','bras_pppoe_linhnt','bras_pppoe_hoand']
    with st.container(border=True):
        st.subheader(':sunny: :green[REPORTING]')
    col29, col30 = st.columns([1,1])
    with col29:
        with st.container(border=True):
            instance_report = st.selectbox(':orange[Select your instance for reporting]', list_instance_avail_from_blaster)
    # run_report_sc, run_report = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], f'{st.session_state.report}', 'GET', payload_start, '/run_report.json')
    run_report_sc, run_report = CALL_API_BLASTER(blaster_server['ip'], blaster_server['port'], instance_report, 'GET', payload_start, '/run_report.json')
    if run_report_sc == 200:
        report_timestamp = execute_remote_command_use_passwd(blaster_server['ip'], dict_blaster_db_format[blaster_server['ip']].get('user'), dict_blaster_db_format[blaster_server['ip']].get('passwd'), f"stat --printf=%y /var/bngblaster/{instance_report}/config.json | cut -d. -f1")
        st.info(f"*Last run: :orange[{report_timestamp}]*")
        report= json.loads(run_report)
        df= pd.DataFrame.from_dict(report, orient="index") # convert report to dataframe
        with col30:
            with st.container(border=True):
                key_select = st.multiselect(':orange[Select your fields]',df.columns, default=['interfaces', 'sessions', 'streams'], placeholder = 'Select your filed for reporting')
        # st.write(key_select)
        # st.write(list(df.columns))
        col27, col28 = st.columns([1,3])
        with col27:
            with st.container(border=True):
                st.subheader(":label: :green[METRICS]")
        with col28:
            with st.container(border=True):
                st.subheader(":newspaper: :green[TABLES]")
        if key_select:
            for i in key_select:
                x= json.loads(df[i].to_json(orient= 'index'))
                # st.write(x['report'])
                with col27:
                    with st.container(border=True):
                        if isinstance(x['report'], int) or isinstance(x['report'], float) or i == 'version':
                            label= f":orange[**{i}**]"
                            value= "%s"%x['report']
                            delta= f"{i}"
                            st.metric(label= label, value= value, delta=delta)
                with col28:
                    with st.container(border=True):
                        if not (isinstance(x['report'], int) or isinstance(x['report'], float) or i == 'version'):
                            st.write(f":orange[**{i} statistics**]")
                            st.dataframe(x['report'], use_container_width= True)
    else:
        with col30:
            with st.container(border=True):
                st.warning('Report not existed', icon="🚨")
        print('[404] File report.json does not exist')
st.divider()
col25,col27,col26 = st.columns([10,1,1])
if authentication_status:
    if st.session_state.p1 or st.session_state.p2 :
        with col26:
            authenticator.logout(':x:', 'main')
with col27:
    if st.session_state.p2:
        if st.button(":oil_drum:", use_container_width= True):
            st.session_state.p1, st.session_state.p2, st.session_state.p3, st.session_state.p4, st.session_state.p5= True, False, False, False, False
            st.rerun()
################################# For ADMIN ##########################################
if dict_user_db[st.session_state.user] == 'admin' and st.session_state.p2:
    st.divider()
    with col25:
        with st.expander(':green[RESET PASSWORD]'):
            try:
                username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
                st.write(username_of_forgotten_password, '\n', email_of_forgotten_password, '\n' ,new_random_password)
                if username_of_forgotten_password:
                    with open('authen/config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    st.success('New password to be sent securely')
                    # The developer should securely transfer the new password to the user.
                elif username_of_forgotten_password == False:
                    st.error('Username not found')
            except Exception as e:
                st.error(e)
        with st.expander(':green[CREATE USER LOGIN]'):
            try:
                email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
                if email_of_registered_user:
                    with open('authen/config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    conn = sqlite_connect_to_db(db_name)
                    sqlite_insert_user(conn, username_of_registered_user, 'operator')
                    conn.close()
                    st.success('User registered successfully')
            except Exception as e:
                st.error(e)
        with st.expander(':green[EDIT USER PRIVILEGES]'):
            col1, col2= st.columns([1,1])
            with col1:
                with st.container(border=True):
                    st.write(":orange[**DELETE**]")
                    conn = sqlite_connect_to_db(db_name)
                    users= sqlite_fetch_users(conn)
                    st.write(":orange[List users]")
                    st.table(users)
                    list_user=[]
                    for i in users:
                        list_user.append(i[0])
                    user_select= st.selectbox(":orange[User]", list_user)
                    if st.button(":blue[**DELETE_USER**]"):
                        sqlite_delete_user(conn, user_select)
                        st.info(":green[Delete successfully]")
                    conn.close()
            with col2:
                with st.container(border=True):
                    st.write(":orange[**UPDATE**]")
                    conn = sqlite_connect_to_db(db_name)
                    users= sqlite_fetch_users(conn)
                    list_user=[]
                    for i in users:
                        list_user.append(i[0])
                    user_update= st.selectbox(":orange[User update]", list_user)
                    user_class_update= st.selectbox(":orange[User]", user_privilege)
                    if st.button(":blue[**UPDATE**]"):
                        sqlite_update_user_class(conn, user_update, user_class_update)
                        st.info(":green[Update successfully]")
                    conn.close() 
        with st.expander(':green[EDIT BLASTERs]'):
            col1, col2= st.columns([1,1])
            with col1:
                with st.container(border=True):
                    st.write(":orange[**INSERT NEW BLASTER**]")
                    ip = st.text_input(":orange[Blaster IP]")
                    port= st.text_input(":orange[Blaster PORT]", '8001')
                    user_ssh= st.text_input(":orange[User SSH]")
                    passwd_ssh= st.text_input(":orange[Password SSH]", type= 'password')
                    if st.button(":blue[**INSERT_BLASTER**]"):
                        conn = sqlite_connect_to_db(db_name)
                        # sqlite_insert_user(conn, user, user_class)
                        sqlite_insert_blaster(conn, ip, port, user_ssh, passwd_ssh)
                        conn.close()
                        st.info(":green[Insert successfully]")
            with col2:
                with st.container(border=True):
                    st.write(":orange[**DELETE BLASTER**]")
                    delete_blaster = st.selectbox(":orange[Select Delete Blaster IP]", dict_blaster_db_format.keys())
                    if st.button(":blue[**DELETE BLASTER**]"):
                        conn = sqlite_connect_to_db(db_name)
                        sqlite_delete_blaster(conn, delete_blaster)
                        conn.close()
                        st.info(":green[Delete blaster successfully]")
        with st.expander(':green[LOG USERS ACTIONS]'):
            with open('auth.log', 'r') as log:
                logging= log.read()
                st.text_area(':orange[Logging]',logging, height = 400)
        with st.expander(':green[SQLITE DB]'):
            col1, col2= st.columns([1,1])
            with col1:
                with st.container(border=True):
                    st.write(":orange[**ALL TABLEs**]")
                    conn = sqlite_connect_to_db(db_name)
                    list_table= sqlite_get_all_tables(conn)
                    select_table= st.selectbox(":orange[Get Table]", list_table)
                    table_detail= sqlite_fetch_table(conn, select_table)
                    st.table(table_detail)
                    if st.button(":blue[**DELETE_TABLE**]"):
                        sqlite_delete_table(conn, select_table)
                        st.info(":green[Delete successfully]")
                    conn.close()
################################# For user ##########################################
if st.session_state.p2:
    with col25:
        with st.expander(':green[CHANGE YOUR PASSWORD]'):
            try:
                if authenticator.reset_password(st.session_state["username"], fields= {'Form name': ':herb: :orange[CHANGE YOUR PASSWORD]', 'Reset':':herb: :blue[**CHANGE**]'}):
                    with open('authen/config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(f'Your password incorrect. Error: {e}', icon="🚨")
