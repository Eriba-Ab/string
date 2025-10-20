from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import AnalyzedString
from .serializers import AnalyzedStringSerializer
from .utils import parse_nl_query


class StringListCreateView(APIView):
	def get(self, request):
		qp = request.query_params
		filters = {}
		try:
			if qp.get('max_length') is not None:
				filters['length__lte'] = int(qp.get('max_length'))
			if 'word_count' in qp:
				filters['word_count'] = int(qp.get('word_count'))
		except (TypeError, ValueError):
			return Response({'detail': 'Invalid filter values'}, status=status.HTTP_400_BAD_REQUEST)

		queryset = AnalyzedString.objects.filter(**{k: v for k, v in filters.items() if v is not None})
		if 'contains_character' in qp:
			ch = qp.get('contains_character')
			queryset = [q for q in queryset if ch in q.character_frequency_map]

		serializer = AnalyzedStringSerializer(queryset, many=True)
		return Response({
			'data': serializer.data,
			'count': len(serializer.data),
			'filters_applied': qp
		})

	def post(self, request):
		value = request.data.get('value')
		if value is None:
			return Response({'detail': 'Missing "value"'}, status=status.HTTP_400_BAD_REQUEST)
		if not isinstance(value, str):
			return Response({'detail': '"value" must be a string'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
		try:
			obj = AnalyzedString.create_or_raise(value)
		except ValueError:
			return Response({'detail': 'String already exists'}, status=status.HTTP_409_CONFLICT)
		serializer = AnalyzedStringSerializer(obj)
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class StringRetrieveDeleteView(APIView):
	def get(self, request, string_value):
		obj = get_object_or_404(AnalyzedString, value=string_value)
		return Response(AnalyzedStringSerializer(obj).data)

	def delete(self, request, string_value):
		obj = AnalyzedString.objects.filter(value=string_value).first()
		if not obj:
			return Response({'detail': 'String not found'}, status=status.HTTP_404_NOT_FOUND)
		obj.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)


class NaturalLanguageFilterView(APIView):
	def get(self, request):
		q = request.query_params.get('query')
		if not q:
			return Response({'detail': 'Missing query'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			parsed = parse_nl_query(q)
		except ValueError:
			return Response({'detail': 'Unable to parse natural language query'}, status=status.HTTP_400_BAD_REQUEST)

		queryset = AnalyzedString.objects.all()
		if 'is_palindrome' in parsed:
			queryset = queryset.filter(is_palindrome=parsed['is_palindrome'])
		if 'min_length' in parsed:
			queryset = queryset.filter(length__gte=parsed['min_length'])
		if 'contains_character' in parsed:
			queryset = [x for x in queryset if parsed['contains_character'] in x.character_frequency_map]

		serializer = AnalyzedStringSerializer(queryset, many=True)
		return Response({
			'data': serializer.data,
			'count': len(serializer.data),
			'interpreted_query': {'original': q, 'parsed_filters': parsed}
		})