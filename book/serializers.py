from book.models import Book
from rest_framework import serializers

class BookSerializer(serializers.ModelSerializer):
    START = 1000000
    book_id = serializers.SerializerMethodField()
    dimension = serializers.SerializerMethodField()
    class Meta:
        model = Book
        exclude = ["description"]
    def get_book_id(self, obj):
        return self.START + obj.id
    def get_dimension(self,obj):
        return f"{obj.length} x {obj.breadth} x {obj.height} cm"
class FullBookSerializer(serializers.ModelSerializer):
    START = 1000000
    book_id = serializers.SerializerMethodField()
    dimension = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields="__all__"
    def get_book_id(self, obj):
        return self.START + obj.id
    def get_dimension(self,obj):
        return f"{obj.length} x {obj.breadth} x {obj.height} cm"
