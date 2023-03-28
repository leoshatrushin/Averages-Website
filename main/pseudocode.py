Module Main
	Continue <- 'Y'
	While Continue = 'Y'
		Input (URL)
		Input (User)
		Call URL_Dispatcher(URL, User, HTML, context)
		Output (HTML, context)
		Input (Continue)
	End While
End Module

Module URL_Dispatcher(URL, User, HTML, context)

  Import(Models)

  Length <- len(URL)
  Current_Word <- ''
  Index <- 0
  For Index <- 0 to len(URL)-1
    character <- URL[Index]
    If character = '/' then
      Words[Index] <- Current_Word
      Current_Word <- ''
      Index <- Index + 1
    Else
      Current_Word <- Current_Word + character
    End If
  End For
  Words[Index] <- Current_Word
  If Index = 0 then
    If Is_anonymous(User) then
      Call Choose_Subjects(HTML, context)
    Else
      Call Year_12_Cohort_View(HTML, context)
    End If
  Else
    If Index = 1 then
      If Exists(Subject.Objects.filter(SubjectName = Words[1])) then
        Call Subject_Page_View(User, Words[1], HTML, context)
      Else
        If Exists(User.Objects.filter(UserName = Words[1])) then
          Call User_Page_View(User, Words[1], HTML, context)
        Else
          Call Error_Dispatcher(404, HTML, context)
        End If
      End If
    Else
      If Index = 2 then
        If Exists(Subject.Objects.filter(SubjectName = Words[1])) then
          Stop <- False
          If Exists(Test.Objects.filter(TestName = Words[2])) then
            Call Test_Page_View(User, Words[1], Words[2], HTML, context)
            Stop <- True
          End If
          If Exists(Class.Objects.filter(ClassCode = Words[2])) then
            Call Class_Page_View(User, Words[1], Words[2], HTML, context)
            Stop <- True
          End If
          If Exists(User.Objects.filter(UserName = Words[2])) then
            Call Class_Page_View(User, Words[1], Words[2], HTML, context)
            Stop <- True
          End If
          If Words[2] = 'update_marks' then
            Call Update_Marks_View(User, Words[1], HTML, context)
            Stop <- True
          End If
          If NOT Stop then
            Call Error_Dispatcher(404, HTML, context)
          End If
        Else
          Call Error_Dispatcher(404, HTML, context)
        End If
      Else
        Call Error_Dispatcher(404, HTML, context)
      End If
    End If
  End If
End Module

Module Models

  Import(models from django.db)
  Import(User from django.contrib.auth.models)

  Class Subject(models.Model)
    name <- models.CharField(max_length<-30)
    students <- models.ManyToManyField(User, blank<-True)
    gives_atar_bonus <- models.BooleanField(null<-True)
  End Class

  Class Class(models.Model)
    subject <- models.ForeignKey(Subject, on_delete<-models.CASCADE)
    students <- models.ManyToManyField(User, blank<-True)
    code <- models.CharField(max_length<-30)
    teacher <- models.CharField(max_length<-30)
    people <- models.IntegerField(null<-True)
    description <- models.CharField(max_length<-50, null<-True)
  End Class

  Class Test(models.Model)
    name <- models.CharField(max_length<-200)
    short_name <- models.CharField(max_length<-200, null<-True)
    marks_out_of <- models.IntegerField()
    weighting <- models.DecimalField(decimal_places<-2,max_digits<-5)
    order <- models.IntegerField()
    subject <- models.ForeignKey(Subject, on_delete<-models.CASCADE)
    has_happened <- models.BooleanField(null<-True)
    is_exam <- models.BooleanField(null<-True)
  End Class

  Class Mark(models.Model)
    value <- models.DecimalField(decimal_places<-1,max_digits<-4)
    test <- models.ForeignKey(Test, on_delete<-models.CASCADE, null<-True)
    student <- models.ForeignKey(User, on_delete<-models.CASCADE, null<-True)
  End Class

  Class Average(models.Model)
    student <- models.ForeignKey(User, on_delete<-models.CASCADE)
    subject <- models.ForeignKey(Subject, on_delete<-models.CASCADE)
    value <- models.DecimalField(decimal_places<-10,max_digits<-13)
  End Class

  Class Rank(models.Model):
    student <- models.ForeignKey(User, on_delete<-models.CASCADE)
    subject <- models.ForeignKey(Subject, on_delete<-models.CASCADE)
    value <- models.IntegerField()
  End Class

End Module

Module Subject_Page_View(User, Subject, HTML, context)

  Import(Models)

  rank_objects <- Rank.objects.filter(subject=subject).order_by('value')
  For Index <- 0 to len(ranks)-1
    students[Index] <- rank_objects[Index]['student']
    ranks[Index] <- rank_objects[Index]['value']
  End For

  test_objects <- Test.objects.filter(subject=subject).order_by('date')
  For Index <- 0 to len(test_objects)-1
    test_totals[Index] <- 0
    test_top_marks[Index] <- 0
    test_students[Index2] <- 0
  Index <- 0
  For Index3 <- 0 to len(students)-1
    student <- students[Index3]
    Index2 <- 0
    For Index4 <- 0 to len(test_objects)-1
    	test <- test_objects[Index4]
      If test['date'] < Current_Date() then
        result <- Mark.objects.filter(student=student, test=test)
        If Exists(result) then
          result = Mark.objects.get(student=student,test=test)['value']/test['marks_out_of']
          student_results[Index][Index2] <- String(Round(100*result, 2)) + '%'
          test_totals[Index2] <- test_totals[Index2] + result
          If result > test_top_marks[Index2] then
            test_top_marks[Index2] <- result
          End If
          test_students[Index2] <- test_students[Index2] + 1
        Else
          student_results[Index][Index2] <- ''
        End If
      Else
        student_results[Index][Index2] <- ''
      End If
      Index2 <- Index2 + 1
    Index <- Index + 1
    End For
  End For

  For Index <- 0 to len(students)-1
    averages[Index] <- Average.objects.get(subject=subject, student=student)['value']
  End For
  sum <- 0
  For Index <- o to len(averages)-1
  	average <- averages[Index]
    sum <- sum + average
  End For
  year_average <- String(Round(100*sum/len(averages), 2)) + '%'
  For Index <- 0 to len(averages)
    averages[Index] <- String(Round(100*averages[Index], 2)) + '%'
  End For

  headers[0], headers[1] <- 'Rank', 'Name'
  Index <- 2
  For Index2 <- 0 to len(test_objects)-1
  	test <- test_objects[Index2]
    headers[Index] <- test['short_name']
    Index <- Index + 1
  End For
  headers[Index] <- "Average"

  top_marks[0] <- "Top Mark"
  Index <- 1
  For Index2 <- 0 to len(test_top_marks)-1
  	top_mark <- test_top_marks[Index2]
    If top_mark = 0 then
      top_marks[Index] <- ''
    Else
      top_marks[Index] <- String(Round(100*top_mark, 2)) + '%'
    End If
    Index <- Index + 1
  End For

  test_averages[0] <- 'Average'
  For Index <- 0 to len(test_objects)-1
    If test_students = 0 then
      test_averages[Index] <- ''
    Else
      test_averages[Index] <- String(Round(100*(test_totals[Index]/test_students[Index]), 2)) + '%'
    End If
  End For

  tests[0] <- ''
  Index <- 1
  For Index2 <- 0 to len(test_objects)-1
  	test <- test_objects[Index2]
    tests[Index] <- test['short_name']
    Index <- Index + 1
  End For

  Table1Data[0] <- ranks
  Table1Data[1] <- students
  Table1Data[2] <- student_results
  Table1Data[3] <- averages
  
  Table2Data[0] <- tests
  Table2Data[1] <- test_averages
  Table2Data[2] <- test_top_marks

  HTML <- 'main/subject page.html'
  context <- {'subject': subject, 'year_average': year_average, 'data0': data0, 'headers': headers, 'data': data, 'class': student_class}

End Module

Module Update_Marks_View(response, User, Subject, HTML, context)

  Import(Models)
  Import(Forms)

  subject = Subject.objects.get(SubjectName=Subject)
  If subject in User.subject_set.all() then
    If response['method'] = "POST" then
      form <- UpdateMarks(response['POST'], subject)

      If Is_valid(form) then
        test_objects <- subject.test_set.all().order_by('order')
        For Index <- 0 to Length(test_objects)-1
          score <- form[Index]
          If score then
            mark <- Mark.objects.filter(test=test_objects[Index], student=user)
            If Exists(mark) then
              mark <- Mark.objects.get(test=test_objects[Index], student=user)
            Else
              mark <- Mark(value<-score, test<-test_objects[Index], student<-user)
            End If

            Save(mark)
          End If
        End For

        student_marks <- Mark.objects.filter(student=user, test__subject=subject)
        weighted_sum, weighting_sum <- 0, 0

        For Index <- 0 to len(student_marks)-1
        	mark <- student_marks[Index]
          weighted_sum <- weighted_sum + mark['test']['weighting'] * (mark['value']/mark['test']['marks_out_of'])
          weighting_sum <- weighting_sum + mark['test']['weighting']
        End For
        weighted_average <- weighted_sum/weighting_sum
        average = Average.objects.filter(subject=subject, student=user)
        If Exists(average) then
          average <- Average.objects.get(subject=subject, student=user)
          average['value'] = weighted_average
        Else
          average <- Average(student<-user, subject<-subject, value<-weighted_average)
        End If

        Save(average)

        Call Update_Ranks(Subject)

      End If
      Call User_Subject_Page(User, Subject, HTML, context)
    Else
      form <- UpdateMarks(subject)
      test_objects <- Test.Objects.filter(subject=subject)
      For Index <- 0 to len(test_objects)-1
        marks_list[Index] <- test_objects[Index]['marks_out_of']
      End For
      
      FHTML <- 'main/update_marks.html'
      Fcontext <- {"form": form, "marks_list": marks_list}

    End If
  Else
    Call Error_Dispatcher(403, HTML, context)
  End If
End Module

Module Update_Ranks(Subject)

  averages <- Average.objects.filter(subject=subject)
  For counter <- 0 to len(averages)-1
  	average <- averages[counter]
    greater_averages <- averages.filter(value>average_value)
    rank <- Rank.objects.filter(student=average['student'], subject=subject)
    If Exists(rank) then
      rank <- Rank.objects.get(student=average['student'], subject=subject)
      rank['value'] <- len(greater_averages)+1
    Else
      rank <- Rank(subject<-subject, student<-average['student'], value<-len(greater_averages)+1)
    End If
    Save(rank)
  End For
End Module

Module User_Page_View(User, UserDisplayed, HTML, context)

  Import(Models)

  If User != UserDisplayed then
    Call Error_Dispatcher(403, HTML, context)
  Else
    rank_objects <- Rank.objects.filter(student=CUser).order_by('-value')
    Index <- 0
    sum_7_ranks, sum_6_ranks, sum_5_ranks, sum_4_ranks <- 0, 0, 0, 0
    For Index <- 0 to 6
    	rank <- rank_objects[Index]
      sum_7_ranks <- sum_7_ranks + rank['value']
      Case Index of
      	< 4: sum_4_ranks <- sum_4_ranks + rank['value']
      	= 4: sum_5_ranks <- sum_4_ranks + rank['value']
      	= 5: sum_5_ranks <- sum_5_ranks + rank['value']
      End Case
      Index <- Index + 1
    End For
    average_objects <- Average.objects.filter(student=user).order_by('-value')
    Index <- 0
    sum_7_average, sum_6_average, sum_5_average, sum_4_average <- 0, 0, 0, 0
    For Index <- 0 to 6
    	average <- average_objects[Index]
      sum_7_average <- sum_7_average + average['value']
      Case Index of
      	< 4: sum_4_average <- sum_4_average + average['value']
      	= 5: sum_5_average <- sum_4_average + average['value']
      	= 6: sum_6_average <- sum_5_average + average['value']
      End Case
      Index <- Index + 1
    End For
    total_7_average = String(Round(100*sum_7_average/7, 2)) + '%'
    total_6_average = String(Round(100*sum_6_average/6, 2)) + '%'
    total_5_average = String(Round(100*sum_5_average/5, 2)) + '%'
    total_4_average = String(Round(100*sum_4_average/4, 2)) + '%'
    TEA <- sum_4_average
    For Index <- 0 to len(student_averages)-1
    	average <- student_averages[Index]
      If average['subject']['gives_atar_bonus'] = True then
        If average >= 0.5 then
          TEA += average*0.1
        End If
      End If
    End For
    TEA <- String(Round(100*TEA, 2))
  max_tests <- 0
  For subject in user.subject_set.all()
    num_tests <- len(Test.objects.filter(subject=subject))
    If num_tests > max_tests then
      max_tests <- num_tests
    End If
  End For
  For Index <- 0 to max_tests
    Table1Data[0][Index] <- ''
  End For
  Table1Data[0][max_test+1], Table1Data[0][max_test+2], Table1Data[0][max_test+3] <- "Average", "Rank", "Top Average"
  Table1Data[1]
  Index <- 1
  For subject in user.subject_set.all().order_by('name')
    Table1Data[Index][0] <- subject['SubjectName']
    Index2 <- 1
    For mark in Mark.objects.filter(test__subject=subject, student=user).order_by('test__date')
      Table1Data[Index][Index2] <- String(Round(100*mark['value']/mark['test']['marks_out_of']), 2) + '%'
      Index2 <- Index2 + 1
    End For
    For Index3 <- 0 to max_tests-len(Test.objects.filter(subject=subject))-1
      Table1Data[Index][Index2] <- ''
      Index2 <- Index2 + 1
    End For
    Table1Data[Index][Index2] <- String(Round(100*Average.objects.get(subject=subject, student=user)['value'], 2)) + '%'
    Table1Data[Index][Index2+1] <- Rank.objects.get(subject=subject, student=user)['value']
    Table1Data[Index][Index2+2] <- String(Round(100*Average.objects.filter(subject=subject).order_by('-value')[0]['value'], 2)) + '%'
    Index <- Index + 1
  End For

  HTML <- 'main/user page.html'
  context <- {'Table1Data': Table1Data, 'sum_7_ranks': sum_7_ranks, 'sum_6_ranks': sum_6_ranks, 'sum_5_ranks': sum_5_ranks, 'sum_4_ranks': sum_4_ranks, 'total_7_average', 'total_6_average': total_6_average, 'total_5_average': total_5_average, 'total_4_average': total_4_average, 'atar': atar, 'TEA': TEA}
End Module

Module User_Subject_Page(User, UserDisplayed, subject, HTML, context)

  Import(Models)

  If User = UserDisplayed then
    mark_objects <- Mark.objects.filter(student=user, test__subject=subject).order_by('test__date')
    For mark_index <- 0 to Length(mark_objects)
      mark <- mark_objects[mark_index]
      marks[mark_index] <- [mark['value']/mark['test']['marks_out_of']
    EndFor
    average_object <- Average.objects.filter(student=user, subject=subject)
    average <- average_object['value']
    rank_object =<- Rank.objects.filter(student=user, subject=subject)
    rank <= rank_object['value']
    test_objects <- Test.objects.filter(student=user, subject=subject)
    
    future_w_sum <- 0
    total_w_sum <-0
    For counter <- 0 to len(test_objects)-1
    	test <- test_objects[counter]
      w <- test['weighting']
      total_w_sum <- total_w_sum + w
      If test['has_happened'] = False
        future_w_sum <- future_w_sum + w
      EndIf
    EndFor

    marksum <- average/100 * (total_w_sum - future_w_sum)/total_w_sum

    maximum_pos_average <- 100*(marksum + future_w_sum)/total_w_sum

    index, sum_marks, sum_weights <- 0, 0, 0
    For counter <- 0 to len(mark_objects)-1
    	mark <- mark_objects[0]
      sum_marks += mark['value']*mark['test']['weighting']/mark['test']['marks_out_of']
      sum_weights += mark['test']['weighting']
      linechartmarks[index] <- 100*mark['value']/mark['test']['marks_out_of']
      linechartaverages[index] <- 100*sum_marks/sum_weights
      index <- index + 1
    EndFor

    num_tests <- len(linechartmarks)
    X <- (num-1)/2
    Y1, Y2 <- 0, 0
    For Index <- 0 to len(linechartmarks)-1
    	mark <- linechartmarks[Index]
      Y1 <- Y1 + mark
    EndFor
    For Index <- 0 to len(linechartaverages)-1
    	average <- linechartaverages[Index]
      Y2 <- Y2 + average
    EndFor
    Y1, Y2 <- Y1/num, Y2/num
    numerator1, numerator2, denominator <- 0, 0, 0
    For counter <- 0 to num
      numerator1 <- numerator1 + (counter-X)*linechartmarks[counter]-Y1)
      denominator <- denominator + (counter-X)^2
    EndFor
    For counter <- 0 to num
      numerator2 <- numerator2 + (counter-X)*(linechartaverages[counter]-Y2)
    EndFor
    m1, m2 <- numerator1/denominator, numerator2/denominator
    a1, a2 <- Y1-m1*X, Y2-m2*X
    b1, b2 <- a1+m1*num, a2+m2*num

    If b2 > 100
      predicted_average <- 100
    Else
      If b2 < 0
        predicted_average <- 0
      Else
        predicted_average <- b2

    For index <- 0 to len(test_objects)
      linechartlabels[index] <- test_objects[index]['short_name']
    EndFor

    For index <- 0 to len(test_objects)
      test <- test_objects[index]
      If Exists(Mark.objects.filter(test=test, student=active_user)) then
        test_datas[index] <- [test['name'], test['weighting'], test['marks_out_of'], mark_objects[index]['value'], marks[index]]
      Else
        test_datas += [[test['name'], test['weighting'], test['marks_out_of'], 0, 0]]
      EndIf
    EndFor

    rank_objects <- Rank.objects.filter(subject=subject).order_by('value')
    For index <- 0 to len(rank_objects)
      ranked_students[index] <- rank_objects[index]['student']
      user_rank <- Index(ranked_students, user)
      offset = len(ranked_students)-user_rank
      before, after = 3, 2
      If affset <= after then
        factor <- after-offset+1
        after <- after-factor
        before <- before+factor
      Else
        If user_rank < before
          factor <- before-user_rank
          after <- after+factor
          before <- before-factor
      user_number <- before + 2
      If 0 >= user_rank-before then
        lower <- 0
      Else
        lower <- user_rank-before
      EndIf
      If len(ranked_stuents) <= user_rank+after+1
        upper <- len(ranked_students)
      Else
        upper <- user_rank+after+1
      EndIf
      counter <- 0
      For index <- lower to upper
        student <- ranked_students[index]
        table_col1_rank[counter] <- Index(ranked_students, student)
        table_col2_name[counter] <- student['username']
        table_col3_average[counter] <- Average.objects.get(subject=subject, student=student)['value']
        counter <- counter + 1
      EndFor

      HTML <- 'main/user subject page.html'
      context <- {'user_number': user_number, 'table_data': table_data, 'num': num, 'predicted': predicted, 'test_datas': test_datas, 'linechartlabels': linechartlabels, 'user': user, "subject": subject, "marks": marks, "average": round(average, 1), "rank": rank, 'maximum_possible_average': maximum_possible_average, 'linechartdata': linechartdata, 'trendlinedata': trendlinedata}
      Output(HTML, context)
  Else
    Call Error_Dispatcher(403, HTML, context)
  End If
End Module

Module Forms

  Import(forms from django)
  Import(Models)

  Class ChooseSubjects(forms.Form)
    Module Initiate(self)
      subject_objects <- Subject.objects.all()
      For Index <- 0 to len(subject_objects)-1
        self['fields'][Index] <- forms.BooleanField(label<-subject_objects[Index]['SubjectName'], required<-False)
      End For
    End Module
  End Class

  Class ChooseClasses(forms.Form):
    Module Initiate(self, user)
      self['user'] <- user
      subject_objects <- self['user'].subject_set.all()
      For Index1 <- 0 to len(subject_objects)-1
        class_objects <- Class.objects.filter(subject=subject)
        For Index2 <- 0 to len(class_objects)-1
          self['fields'][String(Index1) + '_' + String(Index2)] <- forms.BooleanField(label<-class_['code'], required<-False)
        End For
      End For
    End Module
  End Class

  Class UpdateMarks(forms.Form)
    Module Initiate(self, subject)
      self['subject'] <- subject
      test_objects <- self['subject'].test_set.all().order_by('order')
      For Index <- 0 to len(test_objects)-1
        self['fields'][Index] <- forms.DecimalField(label<-test['name'], required<-False, decimal_places<-1, max_digits<-4)
      End For
    End Module
  End Class

  Class Settings(forms.Form)
    Module Initiate(self)
      self['fields']['ShowMarks'] <- forms.BooleanField(label<-'Show marks to everyone', required<-False)
    End Module
  End Class

End Module

Module Error_Dispatcher(Error, HTML, context)
  HTML <- 'main/error' + String(Error)
  context <- {}
End Module

Module Choose_Subjects(response, User, HTML, context)
  
  Import(Models)
  Import(Forms)

  If response['method'] = "POST" then
    form <- ChooseSubjects(response['POST'])

    If Is_Valid(formis_valid) then
      subject_objects <- Subject.objects.all()
      Index <- 0
      Repeat
      	If form[Index] then
          subject <- subject_objects[Index]
          Add(subject['students'], user)
          Add(user['subject_set'], subject)
        End If
        Index <- Index + 1
      Until Index = len(subject_objects)
    End If
    Call Choose_Classes(response, User)
    Output(HTML, context)

  Else
    form <- ChooseSubjects()
    HTML <- 'main/choose_subjects.html'
    context <- {'form':form}
  End If
End Module

Module Choose_Classes(response, User, HTML, context)

  Import(Models)
  Import(Forms)

  If response['method'] = 'POST' then
    form <- ChooseClasses(response['POST'], user)

    If Is_Valid(form) then
      subject_objects <- user.subject_set.all()
      For Index1 <- 0 to len(subject_objects) - 1
        class_objects <- subject.class_set.all()
        For Index2 <- 0 to len(class_objects) - 1
          If form['cleaned_data'][String(Index1) + '_' + String(Index2)] then
            class <- class_objects[Index2]
            Add(user['class_set'], class)
            class['people'] <- class['people'] + 1
            Save(class)
          End If
        End For
      End For
      Call User_Page_View(User, HTML, context)

    End If
    
  Else
    form <- ChooseClasses(user<-user)
    HTML <- 'main/choose_classes.html'
    context <- {'form': form}
  End If
End Module