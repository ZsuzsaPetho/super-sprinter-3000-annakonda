from flask import Flask, render_template, redirect, request, url_for


def get_table_from_file(file_name):
    with open(file_name, "r") as file:
        lines = file.readlines()
    table = [element.replace("\n", "").split(";") for element in lines]
    return table


def get_selected_from_table(table, row):
    return table[row][-1].split(",")


def status_re_converter(status):
    if status == "selected,,,,":
        return "Planning"
    elif status == ",selected,,,":
        return "TODO"
    elif status == ",,selected,,":
        return "In Progress"
    elif status == ",,,selected,":
        return "Review"
    elif status == ",,,,selected":
        return "Done"


def status_converter(status):
    if status == "pla":
        return "selected,,,,"
    elif status == "todo":
        return ",selected,,,"
    elif status == "prog":
        return ",,selected,,"
    elif status == "review":
        return ",,,selected,"
    elif status == "done":
        return ",,,,selected"


def write_table_to_file(file_name, table):
    with open(file_name, "w") as file:
        for record in table:
            row = ';'.join(record)
            file.write(row + "\n")


def line_in_file(file_name):
    with open(file_name, "r") as file:
        return sum(1 for line in file if line.rstrip('\n'))


def line_in_table(table):
    return sum(1 for line in table)


def write_row_to_file(file_name, list_):
    row = ';'.join(list_)
    with open(file_name, "a") as file:
        file.write(row + "\n")


def update_row_in_table(table, story_id, story_data):
    for i in range(len(table)):
                if table[i][0] == str(story_id):
                    table[i] = story_data
    return table


def joining_data_from_submit(story_id, label_list, stat):
    return [str(story_id)] + [request.form[item].replace("\r\n", " ") for item in label_list] + [status_converter
                                                                                                 (request.form[stat])]


def renumbering(table):
    for i in range(len(table)):
        table[i][0] = str(i+1)
    return table


def status_reconverted_table(table):
    for i in range(len(table)):
        table[i][-1] = status_re_converter(table[i][-1])
    return table

app = Flask(__name__)


@app.route('/story', methods=['GET', 'POST'])
@app.route('/story/<int:story_id>', methods=['GET', 'POST'])
def route_index(story_id=None):
    file_name = "data.csv"
    if story_id:
        if story_id > line_in_file(file_name):
            return "The given ID does not exist"
        title = "Edit Story"
        action = "/story/" + str(story_id)
        value_list = get_table_from_file(file_name)
        if request.method == 'GET':
            status_list = get_selected_from_table(value_list, story_id-1)
            return render_template('form.html', title=title, action=action, button="Update",
                                   story_title=value_list[story_id-1][1],
                                   user_story=value_list[story_id-1][2],
                                   acc_crit=value_list[story_id-1][3],
                                   b_value=int(value_list[story_id-1][4]),
                                   estimation=float(value_list[story_id-1][5]),
                                   status=status_list)
        elif request.method == 'POST':
            story_data = joining_data_from_submit(str(story_id),
                                                  ['story_title', 'user_story', 'acc_crit', 'b_value', 'estimation'],
                                                  'status')
            table = update_row_in_table(get_table_from_file(file_name), story_id, story_data)
            write_table_to_file(file_name, table)
            return redirect(url_for('route_index'))
    else:
        title = "Add New Story"
        action = "/story"
        if request.method == 'POST':
            story_data = joining_data_from_submit(1 + line_in_file(file_name),
                                                  ['story_title', 'user_story', 'acc_crit', 'b_value', 'estimation'],
                                                  'status')
            write_row_to_file(file_name, story_data)
    return render_template('form.html', title=title, status=["", "", "", "", ""], button="Create")


@app.route('/')
@app.route('/list')
def route_list():
    value_list = status_reconverted_table(get_table_from_file("data.csv"))
    return render_template('list.html', table=value_list)


@app.route('/list/<int:story_id>')
def del_list(story_id=None):
    file_name = "data.csv"
    value_list = [line for line in get_table_from_file(file_name) if line[0] != str(story_id)]
    write_table_to_file(file_name, renumbering(value_list))
    return redirect(url_for('route_list'))


if __name__ == "__main__":
    app.secret_key = 'something'
    app.run(
        debug=True,
        port=5002
    )