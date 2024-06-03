#include <iostream>
#include <string>
#include <sstream>
#include <vector>
using namespace std;

template<typename T,typename Predicate>

void addToArrayIfConditionMet(vector<T>& arr,const T& value,Predicate condition)
{
    if(condition(value))
    {
        arr.push_back(value);
    }
}

bool coditionToaddinArray(string x)
{
    //trebuie pus conditie pentru adaugare timp in array: trebuie sa se lege de punctul de pe gps
    return !x.empty();
}

int deltaTime(int timenow,int lasttime)
{
    if(timenow<lasttime)
        return -(lasttime-timenow);
    else
        return timenow-lasttime; 
}

void stringToInts(string& str,int &minutes,int &seconds,int &miliseconds)
{
    stringstream s(str);
    string temp;

    getline(s,temp,':');
    minutes=stoi(temp);

    getline(s,temp,':');
    seconds=stoi(temp);

    getline(s,temp);
    miliseconds=stoi(temp);
}


int convertToMiliseconds(int minutes,int seconds,int miliseconds)
{
    return (minutes*60000)+(seconds*1000)+miliseconds;
}

string convertToMinutesandtoString(int time)
{
    int minutes = time/(60 * 1000);
    int seconds = (time % (60*1000))/1000;
    int remainingMiliseconds = time % 1000;
    ostringstream s;
    s<<minutes<<":"<<seconds<<":"<<remainingMiliseconds;
    return s.str();
}

int main()
{
    vector<string> myArray;
    
    string input="12:34:567";
    string input2="12:33:566";
    int minutes,seconds,miliseconds;

    stringToInts(input,minutes,seconds,miliseconds);
    int time1=convertToMiliseconds(minutes,seconds,miliseconds);

    stringToInts(input2,minutes,seconds,miliseconds);
    int time2=convertToMiliseconds(minutes,seconds,miliseconds);   

    int delta=deltaTime(time1,time2);
    string finaltime=convertToMinutesandtoString(delta);
    addToArrayIfConditionMet(myArray,finaltime,coditionToaddinArray);
    for (string val : myArray) {
        cout << val << " ";
    }
    cout << endl;
    return 0;
}