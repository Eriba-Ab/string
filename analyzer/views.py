from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import StringEntry
from .serializers import StringEntrySerializer
from .utils import analyze_string,  parse_natural_language_query

class StringListCreateView(APIView):
    def post(self, request):
        value = request.data.get('value')
        if value is None:
            return Response({'error': 'Missing "value" field'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(value, str):
            return Response({'error': 'Invalid data type for "value"'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        analysis = analyze_string(value)
        if StringEntry.objects.filter(id=analysis['sha256_hash']).exists():
            return Response({'error': 'String already exists'}, status=status.HTTP_409_CONFLICT)

        entry = StringEntry.objects.create(
            id=analysis['sha256_hash'],
            value=value,
            properties=analysis
        )
        return Response(StringEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


    def get(self, request):
        qs = StringEntry.objects.all()
        params = request.query_params
        try:
            if 'is_palindrome' in params:
                val = params['is_palindrome'].lower() == 'true'
                qs = qs.filter(properties__is_palindrome=val)
            if 'min_length' in params:
                qs = [x for x in qs if x.properties['length']
                    >= int(params['min_length'])]
            if 'max_length' in params:
                qs = [x for x in qs if x.properties['length']
                    <= int(params['max_length'])]
            if 'word_count' in params:
                qs = [x for x in qs if x.properties['word_count']
                    == int(params['word_count'])]
            if 'contains_character' in params:
                ch = params['contains_character']
                qs = [x for x in qs if ch in x.value]
        except Exception as e:
            return Response({'error': 'Invalid query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        data = StringEntrySerializer(qs, many=True).data
        return Response({
            'data': data,
            'count': len(data),
            'filters_applied': request.query_params
        }, status=status.HTTP_200_OK)


class StringDetailView(APIView):
    def get(self, request, string_value):
        entry = StringEntry.objects.filter(value=string_value).first()
        if not entry:
            return Response({'error': 'String not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(StringEntrySerializer(entry).data)

    def delete(self, request, string_value):
        entry = StringEntry.objects.filter(value=string_value).first()
        if not entry:
            return Response({'error': 'String not found'}, status=status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NaturalLanguageFilterView(APIView):
	def get(self, request):
		query = request.query_params.get('query')
		if not query:
			return Response({'error': 'Missing query'}, status=status.HTTP_400_BAD_REQUEST)
		filters = parse_natural_query(query)
		if not filters:
			return Response({'error': 'Unable to parse query'}, status=status.HTTP_400_BAD_REQUEST)


		qs = StringEntry.objects.all()
		if 'is_palindrome' in filters:
			qs = qs.filter(properties__is_palindrome=filters['is_palindrome'])
		if 'word_count' in filters:
			qs = [x for x in qs if x.properties['word_count'] == filters['word_count']]
		if 'min_length' in filters:
			qs = [x for x in qs if x.properties['length'] >= filters['min_length']]
		if 'contains_character' in filters:
			qs = [x for x in qs if filters['contains_character'] in x.value]


		data = StringEntrySerializer(qs, many=True).data
		return Response({
    		'data': data,
    		'count': len(data),
    		'interpreted_query': {
       			'original': query,
        		'parsed_filters': filters
    		}
		}, status=status.HTTP_200_OK)
