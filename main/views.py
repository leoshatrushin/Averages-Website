from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import JsonResponse
from django.contrib.auth.models import User, Group

atar_lookup_dictionary = {
    407.1: '99.95',
    396.5: '99.90',
    391.35: '99.85',
    386.2: '99.80',
    381.05: '99.75',
    375.9: '99.70',
    353: '99',
    320: '97',
    300: '90',
    200: 'ur trash'
}

def intformat1(mark):
    return round(100*mark, 1)

def calculate_average(user, subject, tests_array):
    pass

def calculate_rank(user, subject, tests_array):
    pass

def calculate_atar(TEA):
    for i in atar_lookup_dictionary:
        if TEA >= i:
            return atar_lookup_dictionary[i]

def essential_context(active_user):
    if active_user.is_anonymous:
        return {'active_user': active_user}
    class_codes = list()
    subject_names = list()
    print(active_user.username)
    for subject_ in active_user.subject_set.all():
        subject_names += [subject_.name]
        print(Class.objects.filter(subject=subject_, students=active_user))
        class_codes += [Class.objects.get(subject=subject_, students=active_user).code]
    subjects = zip(subject_names, class_codes)

    return {'active_user': active_user, 'subjects': subjects}

def error(response, code):
    user = response.user
    return render(response, "main/error" + str(code) + ".html", essential_context(user))

def home(response):
    user = response.user
    return render(response, 'main/home.html', essential_context(user))

def choose_subjects(response):
    if response.method == "POST":
        form = ChooseSubjects(response.POST)
        print(response.user.username)
        if form.is_valid(): 
            user = response.user
            for i, subject in enumerate(Subject.objects.all()):
                if form.cleaned_data['%s_field' % i]:
                    subject.students.add(user)
                    group = Group.objects.get(name=subject.name)
                    group.user_set.add(user)

        return redirect("/choose_classes/")

    else:
        form = ChooseSubjects()

    return render(response, "main/choose_subjects.html", {"form":form})

def choose_classes(response):
    user = response.user
    if response.method == "POST":
        form = ChooseClasses(response.POST, user=user)

        if form.is_valid():

            valid = True
            stop = False

            for i, subject in enumerate(user.subject_set.all()):
                count = 0
                if stop:
                    break
                for j, class_ in enumerate(subject.class_set.all()):
                    if form.cleaned_data['%s_%s_field' % (i, j)]:
                        count += 1
                        if count == 2:
                            valid = False
                            stop = True
                            break
                if count == 0:
                    valid = False
                    break

            if valid:
                for i, subject in enumerate(user.subject_set.all()):
                    for j, class_ in enumerate(subject.class_set.all()):
                        if form.cleaned_data['%s_%s_field' % (i, j)]:
                            user.class_set.add(class_)
                            class_.people += 1
                            class_.save()
            else:
                return render(response, 'main/choose_classes.html', {'form': form, 'error': 1})

        return redirect("/")
    else:
        form = ChooseClasses(user=user)
    return render(response, 'main/choose_classes.html', {'form': form, 'error': 0})

def settings(response):
    user = response.user
    if response.method == "POST":
        form = Settings(response.POST)

        if form.is_valid():
            pass

    else:
        form = Settings()

    return render(response, 'main/settings.html', {'form': form})

def test(response):
    return render(response, 'main/test.html', {'active_user': response.user})

def update_ranks(subject):
    averages = Average.objects.filter(subject=subject)
    for average in averages:
        greater_averages = averages.filter(value__gt=average.value)
        rank = Rank.objects.filter(student=average.student, subject=subject)
        if rank.exists():
            rank = Rank.objects.get(student=average.student, subject=subject)
            rank.value = len(greater_averages)+1
        else:
            rank = Rank(subject=subject, student=average.student, value=len(greater_averages)+1)
        rank.save()

def user_subject_page(response, subject_name, user_name):
    subject = Subject.objects.get(name=subject_name)
    user = User.objects.get(username=user_name)
    active_user = response.user

    if not active_user.is_anonymous:
        if subject in active_user.subject_set.all():

            mark_objects = Mark.objects.filter(student=user, test__subject=subject).order_by('test__order')
            marks = [round(100*(mark.value/mark.test.marks_out_of), 2) for mark in mark_objects]
            average_object = Average.objects.filter(student=user, subject=subject)
            if average_object.exists():
                average_object = Average.objects.get(student=user, subject=subject)
                average = round(100*average_object.value, 2)
                rounded_average = round(average, 1)
            else:
                rounded_average = ""
            rank_object = Rank.objects.filter(student=user, subject=subject)
            if rank_object.exists():
                rank = Rank.objects.get(student=user, subject=subject).value
            else:
                rank = ""

            maximum_possible_average = 0
            for test in Test.objects.filter(subject=subject):
                if Mark.objects.filter(test=test, student=active_user).exists():
                    mark = Mark.objects.get(test=test, student=active_user)
                    maximum_possible_average += float(mark.value*mark.test.weighting/mark.test.marks_out_of)
                else:
                    maximum_possible_average += float(test.weighting)
            maximum_possible_average /= sum(float(test.weighting) for test in Test.objects.filter(subject=subject))
            maximum_possible_average = str(round(100*maximum_possible_average, 1)) + "%"

            sum_marks = 0
            sum_weights = 0
            linechartdata = [[], []]
            for mark in Mark.objects.filter(test__subject=subject, student=active_user).order_by('test__order'):
                sum_marks += mark.value*mark.test.weighting/mark.test.marks_out_of
                sum_weights += mark.test.weighting
                linechartdata[0] += [100*sum_marks/sum_weights]
                linechartdata[1] += [100*mark.value/mark.test.marks_out_of]

            num = len(linechartdata[0])
            if num != 0:
                X=sum(i for i in range(0, num))/num
                Y1=float(sum(linechartdata[0])/num)
                Y2=float(sum(linechartdata[1])/num)
            else:
                X,Y1,Y2=0,0,0
            counter = 0
            numerator1, numerator2, denominator = 0, 0, 0
            for value in linechartdata[0]:
                numerator1 += (counter-X)*(float(value)-Y1)
                denominator += (counter-X)**2
                counter += 1
            counter = 0
            for value in linechartdata[1]:
                numerator2 += (counter-X)*(float(value)-Y2)
                counter += 1
            if denominator != 0:
                m1, m2 = numerator1/denominator, numerator2/denominator
            else:
                m1, m2 = 0, 0
            a1, a2 = Y1-m1*X, Y2-m2*X
            b1, b2 = a1+m1*num, a2+m2*num
            trendlinedata = [[a1, b1], [a2, b2]]
            linechartdata[0], linechartdata[1] = [round(value, 1) for value in linechartdata[0]], [round(value, 1) for value in linechartdata[1]]

            linechartlabels = [test.short_name for test in Test.objects.filter(subject=subject).order_by('order')]

            predicted = round(trendlinedata[0][1], 1)
            if predicted > 100:
                predicted = 100
            if predicted < 0:
                predicted = 0

            test_datas = []
            for test in Test.objects.filter(subject=subject).order_by('order'):
                if Mark.objects.filter(test=test, student=active_user).exists():
                    test_datas += [[test.short_name, test.weighting, format1(Mark.objects.get(test=test, student=active_user).value/test.marks_out_of), round(Mark.objects.get(test=test, student=active_user).value, 0), test.marks_out_of]]
                else:
                    test_datas += [[test.short_name, test.weighting, 0, 0, test.marks_out_of]]

            #name, average, rank : then implement up and down arrows
            ranked_students = [rank.student for rank in Rank.objects.filter(subject=subject).order_by('value')]
            print(ranked_students)
            if active_user in ranked_students:
                user_rank = ranked_students.index(active_user)
                offset = len(ranked_students)-user_rank
                before, after = 3, 2
                if offset <= after:
                    factor = after-offset+1
                    after -= factor
                    before += factor
                elif user_rank < before:
                    factor = before-user_rank
                    after += factor
                    before -= factor
                user_number = user_rank+2
                table_data = [[Rank.objects.get(subject=subject, student=student).value, student.username, format1(Average.objects.get(subject=subject, student=student).value)] for student in ranked_students[max(0, user_rank-before):min(len(ranked_students), user_rank+after+1)]]
                min_index = 1 + max(0, user_rank-before)
                max_index = min(len(ranked_students), user_rank+after+1)
            else:
                user_number = ""
                table_data = ""

            return render(response, 'main/user subject page.html', {**{'user_number': user_number, 'table_data': table_data, 'num': num, 'predicted': predicted, 'test_datas': test_datas, 'linechartlabels': linechartlabels, 'user': user, "subject": subject, "marks": marks, "average": rounded_average, "rank": rank, 'maximum_possible_average': maximum_possible_average, 'linechartdata': linechartdata, 'trendlinedata': trendlinedata}, **essential_context(active_user)})
        return error(response, 403)
    else:
        return error(response, 403)

def update_marks(response, subject_name):
    subject = Subject.objects.get(name=subject_name)
    user = response.user
    if subject in response.user.subject_set.all():
        if response.method == "POST":
            form = UpdateMarks(response.POST, subject=subject, user=user)

            if form.is_valid():
                user = response.user
                for i, test in enumerate(subject.test_set.filter(has_happened=True).order_by('order')):
                    score = form.cleaned_data['%s_field' % i]
                    if score:
                        mark = Mark.objects.filter(test=test, student=user)
                        if mark.exists():
                            mark = Mark.objects.get(test=test, student=user)
                            print(score)
                            mark.value = score
                        else:
                            mark = Mark(value=score, test=test, student=user)                           
                        mark.save()

                student_marks = Mark.objects.filter(student=user, test__subject=subject)
                weighted_sum, weighting_sum = 0, 0

                for mark in student_marks:
                    weighted_sum += float(mark.test.weighting) * float(mark.value)/float(mark.test.marks_out_of)
                    weighting_sum += mark.test.weighting
                if weighting_sum != 0:
                    weighted_average = float(weighted_sum)/float(weighting_sum)
                else:
                    weighted_average = 0
                average = Average.objects.filter(subject=subject, student=user)
                if average.exists():
                    average = Average.objects.get(subject=subject, student=user)
                    average.value = weighted_average
                else:
                    average = Average(student=user, subject=subject, value=weighted_average)
                average.save()

                update_ranks(subject)

                return redirect("/" + str(subject) + "/%s" % response.user.username)

        else:
            form = UpdateMarks(subject=subject, user=user)
            marks_list = [Test.objects.get(subject=subject, order=i).marks_out_of for i in range(1, len(Test.objects.filter(subject=subject))+1)]
            data = zip(form, marks_list)

            return render(response, 'main/update_marks.html', {**{"form": form, "data": data}, **essential_context(user)})

    else:
        return error(response, 403)

"""def year_page(response, subject_name):
    subject = Subject.objects.get(name=subject_name)
    user = response.user
    if (user.is_anonymous) or (subject not in user.subject_set.all()):
        return error(response, 403)

    students = User.objects.filter(subject=subject)
    rank_dict = dict()
    for student in students:
        rank = Rank.objects.filter(subject=subject, student=student)
        if rank.exists():
            rank = Rank.objects.get(subject=subject, student=student)
            rank_dict[rank.value] = rank_dict.get(rank.value, []) + [student]
    sorted_students = [student for i in range(1, len(students)+1) if i in rank_dict for student in rank_dict[i]]
    ranks = [rank.value for rank in Rank.objects.filter(subject=subject).order_by('value')]
    averages = Average.objects.filter(subject=subject).order_by('-value')
    year_average = str(round(100*sum(average.value for average in averages)/len(averages), 2))+"%"
    averages = [round(100*i.value, 2) for i in averages]
    class_ = Class.objects.get(subject=subject, students=user)

    tests = [""] + [test.short_name for test in Test.objects.filter(subject=subject).order_by('order')]
    average_for_each_test = ["Average"]
    top_mark_for_each_test = ["Top mark"]
    for test_name in tests[1:]:
        test = Test.objects.get(short_name=test_name)
        year_marks = Mark.objects.filter(test=test).order_by('-value')
        if len(year_marks) != 0:
            average_mark = 100*sum(mark.value for mark in year_marks)/len(year_marks)/test.marks_out_of
            top_mark = 100*year_marks[0].value/test.marks_out_of
            average_for_each_test += [str(round(average_mark, 2))+"%"]
            top_mark_for_each_test += [str(round(top_mark, 2))+"%"]
        else:
            average_for_each_test += [""]
            top_mark_for_each_test += [""]

    headers = ["Rank", "Name"] + tests[1:] + ["Average"]

    correct_length = len(tests)
    student_results = []
    for student in sorted_students:
        student_result = [student.username]
        student_marks = Mark.objects.filter(test__subject=subject, student=student).order_by('test__order')
        for mark in student_marks:
            student_result += [str(round(100*mark.value/mark.test.marks_out_of, 2)) + "%"]
        while len(student_result) < correct_length:
            student_result += [""]
        student_results += [student_result]

    data0 = zip(ranks, sorted_students, student_results, averages)
    data = [tests, average_for_each_test, top_mark_for_each_test]

    return render(response, 'main/year page.html', {'data0': data0, 'data': data, 'subject': subject, 'class': class_, 'year_average': year_average, 'headers': headers})"""

def class_page(response, subject_name, class_name):
    class_ = Class.objects.get(code=class_name)
    subject = Subject.objects.get(name=subject_name)
    user = response.user
    if Average.objects.filter(subject=subject, student=user).exists():
        student_average = Average.objects.get(subject=subject, student=user).value
        number_greater_in_class = len(Average.objects.filter(subject=subject, student__class=class_, value__gt=student_average))
    else:
        student_average = ""
        number_greater_in_class = len(Average.objects.filter(subject=subject, student__class=class_))
    year_averages = Average.objects.filter(subject=subject)
    class_averages = Average.objects.filter(subject=subject, student__class=class_).order_by('-value')
    class_average = sum(average.value for average in class_averages)/class_.people
    classes_averages = []
    for class__ in Class.objects.filter(subject=subject):
        total = sum(average.value for average in Average.objects.filter(subject=subject, student__class=class__))
        if class_.people != 0:
            classes_averages += [total/class_.people]
        else:
            classes_averages += ["0"]
    classes_averages = list(reversed(sorted(classes_averages)))
    class_rank = classes_averages.index(class_average)+1
    class_average = round(100*class_average, 2)
    if len(year_averages) == 0:
        year_average = 0
    else:
        year_average = round(100*sum(average.value for average in year_averages)/len(year_averages), 2)
    if len(class_averages) != 0:
        class_highest_average = round(100*class_averages[0].value, 2)
        class_highest_rank = Rank.objects.get(student=class_averages[0].student, subject=subject)
    else:
        class_highest_average = 0
        class_highest_rank = 0

    tests = [""] + [test.name for test in Test.objects.filter(subject=subject).order_by('order')]
    class_average_for_each_test = ["Class Average"]
    class_rank_for_each_test = ["Class Rank"]
    class_highest_mark_for_each_test = ["Top mark in class"]
    class_highest_rank_for_each_test = ["Top rank in class"]
    for test_name in tests[1:]:
        test = Test.objects.get(name=test_name)
        class_marks = Mark.objects.filter(test=test, student__class=class_).order_by('-value')
        classes_averages = list(reversed(sorted((sum(mark.value for mark in Mark.objects.filter(test=test, student__class=class__))/len(Mark.objects.filter(test=test, student__class=class__)))/test.marks_out_of if len(Mark.objects.filter(test=test, student__class=class__)) != 0 else 0 for class__ in Class.objects.filter(subject=subject))))
        if len(class_marks) != 0:
            class_average_for_test = (sum(mark.value for mark in class_marks)/len(class_marks))/test.marks_out_of
            class_average_for_each_test += [str(round(100*class_average_for_test, 2))+"%"]
            class_rank_for_each_test += [classes_averages.index(class_average_for_test)+1]
            highest_mark = class_marks[0]
            class_highest_mark_for_each_test += [str(round(100*highest_mark.value/highest_mark.test.marks_out_of, 2))+"% ("+str(highest_mark.student.username)+")"]
            year_marks = [mark.value for mark in Mark.objects.filter(test=test).order_by('-value')]
            class_highest_rank_for_each_test += [year_marks.index(highest_mark.value)+1]
        else:
            class_average_for_each_test += [""]
            class_rank_for_each_test += [""]
            class_highest_mark_for_each_test += [""]
            class_highest_rank_for_each_test += [""]
    tests = [""] + [test.short_name for test in Test.objects.filter(subject=subject).order_by('order')]

    year_ranks = [rank.value for rank in Rank.objects.filter(subject=subject, student__class=class_).order_by('value')]
    students = User.objects.filter(subject=subject, class__code=class_.code)
    rank_dict = dict()
    for student in students:
        rank = Rank.objects.filter(subject=subject, student=student)
        if rank.exists():
            rank = Rank.objects.get(subject=subject, student=student)
            rank_dict[rank.value] = rank_dict.get(rank.value, []) + [student]
    sorted_students = [student for i in range(1, len(year_averages)+1) if i in rank_dict for student in rank_dict[i]]
    tests = [""] + [test.short_name for test in Test.objects.filter(subject=subject, has_happened=True).order_by('order')]
    correct_length = len(tests)
    student_results = []
    for student in sorted_students:
        student_result = [student.username]
        student_marks = Mark.objects.filter(test__subject=subject, student=student).order_by('test__order')
        for mark in student_marks:
            student_result += [str(round(100*mark.value/mark.test.marks_out_of, 2)) + "%"]
        while len(student_result) < correct_length:
            student_result += [""]
        student_results += [student_result]
    sorted_students = [student.username for student in sorted_students]
    averages = [str(round(100*average.value, 2))+"%" for average in Average.objects.filter(subject=subject, student__class=class_).order_by('-value')]
    class_ranks = [1]
    for i in range(1, len(averages)):
        if averages[i] == averages[i-1]:
            class_ranks += class_ranks[i-1]
        else:
            class_ranks += [i+1]
    tests = [""] + [test.short_name for test in Test.objects.filter(subject=subject, has_happened=True).order_by('order')]
    all_tests = [""] + [test.short_name for test in Test.objects.filter(subject=subject).order_by('order')]
    headers = ["Class rank", "Name"] + tests[1:] + ["Average", "Year rank"]
    average_column = max(len(Mark.objects.filter(test__subject=subject, student=student)) for student in students)+3
    rank_column = average_column+1

    data0 = zip(class_ranks, sorted_students, student_results, averages, year_ranks)
    data = [all_tests, class_average_for_each_test, class_rank_for_each_test, class_highest_mark_for_each_test, class_highest_rank_for_each_test]
    print(data)
    return render(response, 'main/class page.html', {**{'average_column': average_column, 'rank_column': rank_column, 'class': class_, 'rank_in_class': number_greater_in_class+1, 'class_rank': class_rank, 'class_average': class_average, 'year_average': year_average, 'class_highest_average': class_highest_average, 'class_highest_rank': class_highest_rank, 'data': data, 'data0': data0, 'headers': headers}, **essential_context(user)})

def format(result):
    return str(round(100*result, 2)) + "%"

def format1(result):
    return str(round(100*result, 1)) + "%"

def get_results(students, subject):
    tests = Test.objects.filter(subject=subject).order_by('order')
    student_results = [[] for i in range(0, len(students))]
    test_totals = [0 for i in range(0, len(tests))]
    test_students = [0 for i in range(0, len(tests))]
    test_top_marks = [0 for i in range(0, len(tests))]
    index = 0
    for student in students:
        index2 = 0
        for test in tests:
            if test.has_happened:
                result = Mark.objects.filter(student=student, test=test)
                if result.exists():
                    result = Mark.objects.get(student=student,test=test).value/test.marks_out_of
                    student_results[index] += [format(result)]
                    test_totals[index2] += result
                    if result > test_top_marks[index2]:
                        test_top_marks[index2] = result
                    test_students[index2] += 1
            else:
                student_results[index] += [""]
            index2 += 1
        index += 1
    return student_results

def rank(scores):
    if len(scores) == 0:
        return []
    ranks = [1]
    for i in range(1, len(scores)):
        if scores[i-1] == scores[i]:
            ranks += [ranks[i-1]]
        else:
            ranks += [i+1]
    return ranks

def year_page(response, subject_name):
    user = response.user
    subject = Subject.objects.filter(name=subject_name)
    if subject.exists():
       subject = Subject.objects.get(name=subject_name)
    else:
        return error(response, 404)

    ranks = Rank.objects.filter(subject=subject).order_by('value')
    students = [rank.student for rank in ranks]
    ranks = [rank.value for rank in ranks]

    tests = Test.objects.filter(subject=subject).order_by('order')
    student_results = [[] for i in range(0, len(students))]
    test_totals = [0 for i in range(0, len(tests))]
    test_students = [0 for i in range(0, len(tests))]
    test_top_marks = [0 for i in range(0, len(tests))]
    index = 0
    for student in students:
        index2 = 0
        for test in tests:
            if test.has_happened:
                result = Mark.objects.filter(student=student, test=test)
                if result.exists():
                    result = Mark.objects.get(student=student,test=test).value/test.marks_out_of
                    student_results[index] += [format(result)]
                    test_totals[index2] += result
                    if result > test_top_marks[index2]:
                        test_top_marks[index2] = result
                    test_students[index2] += 1
                else:
                    student_results[index] += [""]
            else:
                student_results[index] += [""]
            index2 += 1
        index += 1

    averages = [Average.objects.get(subject=subject, student=student).value for student in students]
    if len(averages) != 0:
        year_average = format(sum(averages)/len(averages))
    else:
        year_average = 0
    averages = [format(average) for average in averages]

    headers = ["Rank", "Name"] + [test.short_name for test in tests] + ["Average"]

    student_class = Class.objects.get(subject=subject, students=response.user).code

    data0 = zip(ranks, students, student_results, averages)

    test_top_marks = ["Top mark"] + [format(top_mark) if top_mark != 0 else "" for top_mark in test_top_marks]
    test_averages = ["Average"] + [format(test_totals[i]/test_students[i]) if test_students[i] != 0 else "" for i in range(0, len(tests))]
    tests = [""] + [test.short_name for test in tests]

    data = [tests, test_averages, test_top_marks]

    return render(response, 'main/year page.html', {**{'subject': subject, 'year_average': year_average, 'data0': data0, 'headers': headers, 'data': data, 'class': student_class}, **essential_context(user)})
#314, year: 46 vs 51, 

def class_page2(response, subject_name, class_code):
    user = response.user
    subject = Subject.objects.get(name=subject_name)
    class_ = Class.objects.get(code=class_code)

    class_year_ranks = [rank.value for rank in Rank.objects.filter(subject=subject, student__class=class_).order_by('value')]
    class_ranks = rank(class_year_ranks)

    students = User.objects.filter(class__code=class_code).order_by('value')

    subject_classes = subjects.class_set
    number_of_classes = len(subject_classes)
    classes_totals = [0 for i in range(0, number_of_classes)]
    classes_people = [0 for i in range(0, number_of_classes)]
    index = 0
    for class__ in subjects_classes:
        if class__ == class_:
            class_index = index
        for student in class__.students:
            average = Average.objects.filter(student=student, subject=subject)
            if average.exists():
                classes_averages[index] += average[0].value
                classes_people[index] += 1
        index += 1
    classes_averages = [classes_totals[i]/classes_people[i] for i in range(0, number_of_classes)]
    class_average = classes_averages[class_index]
    class_rank = sorted(classes_averages).index(class_average)+1

    averages = [Average.objects.get(subject=subject, student=student).value for student in User.objects.filter(subject=subject)]
    year_average = format(sum(averages)/len(averages))

def test_page(response, subject_name, test_short_name):
    user = response.user
    test = Test.objects.get(short_name=test_short_name)
    subject = test.subject

    test_marks = Mark.objects.filter(test=test)
    test_average = sum(mark.value/test.marks_out_of for mark in test_marks)/len(test_marks)

    return render(response, 'main/test page.html', {'test': test, 'subject': subject})

def FAQ_page(response):
    user = response.user
    return render(response, 'main/FAQ page.html', essential_context(user))

def EULA_page(response):
    user = response.user
    return render(response, 'main/EULA.html', essential_context(user))

def user_page(response, user_name):
    user = User.objects.get(username = user_name)
    student_ranks = [rank.value for rank in Rank.objects.filter(student=user).order_by('-value')[:6]]
    sum_6_ranks = sum(student_ranks)
    sum_5_ranks = sum(student_ranks[:5])
    sum_4_ranks = sum(student_ranks[:4])
    student_averages = Average.objects.filter(student=user).order_by('-value')
    total_6_average = format(sum(average.value for average in student_averages[:6])/6)
    total_5_average = format(sum(average.value for average in student_averages[:5])/5)
    total_4_average = format(sum(average.value for average in student_averages[:4])/4)
    if len(student_averages) >= 4:
        TEA = float(100*sum(average.value for average in student_averages[:4]))
        for average in student_averages:
            if average.subject.gives_atar_bonus:
                if average.value >= 0.5:
                    TEA += float(average.value)*10
        atar = calculate_atar(TEA)
        TEA = round(TEA, 1)
    else:
        TEA = "Not eligible"
        atar = "Not eligible"
    #results
    try:
        max_tests = max(len(Mark.objects.filter(test__subject=subject, student=user)) for subject in user.subject_set.all())
    except:
        max_tests = 0
    data = [["" for i in range(0, max_tests+1)] + ["Average", "Rank", "Top Average"]]
    for subject in user.subject_set.all().order_by('name'):
        num_marks = len(Mark.objects.filter(test__subject=subject, student=user))
        data += [[subject.name] + ["" for i in range(0, max_tests-num_marks)]]
        count = 0
        for mark in Mark.objects.filter(test__subject=subject, student=user).order_by('test__order'):
            data[-1] += [format(mark.value/mark.test.marks_out_of)]
            count += 1
        if Average.objects.filter(subject=subject, student=user).exists():
            data[-1] += [format(Average.objects.get(subject=subject, student=user).value)] + [Rank.objects.get(subject=subject, student=user).value]
        else:
            data[-1] += ["", ""]
        if Average.objects.filter(subject=subject).exists():
            data[-1] += [format(Average.objects.filter(subject=subject).order_by('-value')[0].value)]
        else:
            data[-1] += [""]
    max_tests += 2
    colour = max_tests + 1
    colourtwo = colour + 1
    #data += [[format(Average.objects.get(subject=subject, student=user).value)] + [Rank.objects.get(subject=subject, student=user).value] + [format(Average.objects.filter(subject=subject).order_by('-value')[1].value)]]
    print(data)
    return render(response, 'main/user page.html', {**{'max_tests': max_tests, 'colour': colour, 'colourtwo': colourtwo, 'data': data, 'sum_6_ranks': sum_6_ranks, 'sum_5_ranks': sum_5_ranks, 'sum_4_ranks': sum_4_ranks, 'total_6_average': total_6_average, 'total_5_average': total_5_average, 'total_4_average': total_4_average, 'atar': atar, 'TEA': TEA}, **essential_context(user)})

def slug_url_dispatcher(response, slug):
    if Subject.objects.filter(name=slug).exists():
        return year_page(response, slug)
    elif User.objects.filter(username=slug).exists():
        return user_page(response, slug)
    else:
        return error(response, 404)

#Users can't have names that are the names of subjects or tests
    """if User.objects.filter(name=other_name).exists():
        return me_page(response, slug1, slug2)"""

def slug_slug_url_dispatcher(response, slug1, slug2):
    if Subject.objects.filter(name=slug1).exists():
        if Class.objects.filter(code=slug2, subject__name=slug1).exists():
            return class_page(response, slug1, slug2)
        elif Test.objects.filter(short_name=slug2.replace("_", " "), subject__name=slug1).exists():
            return test_page(response, slug1, slug2.replace("_", " "))
        elif User.objects.filter(username=slug2, subject__name=slug1).exists():
            return user_subject_page(response, slug1, slug2)
        else:
            return error(response, 404)
    else:
        return error(response, 404)









