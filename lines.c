#include <stdio.h>

#define MAX 1000
int _getline(char s[], int m);

main()
{
	int c,i=0;
	char line[MAX];
	while(_getline(line, MAX) > 0) {
		i++;
	}
	printf("%d\n",i);
}

int _getline(char s[], int m)
{
	int c,i=0;
	while((c=getchar())!=EOF && c!='\n') {
		s[i]=c;
		i++;
	}
	return i;
}
