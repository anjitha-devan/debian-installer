from django.db.models import Sum
from django.utils.timezone import now
from kolibri.auth.models import FacilityUser
from kolibri.core.serializers import KolibriModelSerializer
from kolibri.logger.models import AttemptLog, ContentSessionLog, ContentSummaryLog, ExamAttemptLog, ExamLog, MasteryLog, UserSessionLog, ReportsDataOffline
from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField, JSONField


class ContentSessionLogSerializer(KolibriModelSerializer):

    extra_fields = serializers.JSONField(default='{}')

    class Meta:
        model = ContentSessionLog
        fields = ('pk', 'user', 'content_id', 'channel_id', 'start_timestamp',
                  'end_timestamp', 'time_spent', 'kind', 'extra_fields', 'progress')

class ExamLogSerializer(KolibriModelSerializer):
    progress = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    def get_progress(self, obj):
        return obj.exam.question_count

    def get_score(self, obj):
        return obj.attemptlogs.values_list('item').order_by('completion_timestamp').distinct().aggregate(Sum('correct')).get('correct__sum')

    class Meta:
        model = ExamLog
        fields = ('id', 'exam', 'user', 'closed', 'progress', 'score', 'completion_timestamp')
        read_only_fields = ('completion_timestamp', )

    def update(self, instance, validated_data):
        # This has changed, set the completion timestamp
        if validated_data.get('closed') and not instance.closed:
            instance.completion_timestamp = now()
        return super(ExamLogSerializer, self).update(instance, validated_data)

class MasteryLogSerializer(KolibriModelSerializer):

    pastattempts = serializers.SerializerMethodField()
    totalattempts = serializers.SerializerMethodField()
    mastery_criterion = serializers.JSONField(default='{}')

    class Meta:
        model = MasteryLog
        fields = ('id', 'summarylog', 'start_timestamp', 'pastattempts', 'totalattempts', 'user',
                  'end_timestamp', 'completion_timestamp', 'mastery_criterion', 'mastery_level', 'complete')

    def get_pastattempts(self, obj):
        # will return a list of the latest 10 correct and hint_taken fields for each attempt.
        return AttemptLog.objects.filter(masterylog__summarylog=obj.summarylog).values('correct', 'hinted').order_by('-start_timestamp')[:10]

    def get_totalattempts(self, obj):
        return AttemptLog.objects.filter(masterylog__summarylog=obj.summarylog).count()

class AttemptLogSerializer(KolibriModelSerializer):
    answer = serializers.JSONField(default='{}')
    interaction_history = serializers.JSONField(default='[]')

    class Meta:
        model = AttemptLog
        fields = ('id', 'masterylog', 'start_timestamp', 'sessionlog',
                  'end_timestamp', 'completion_timestamp', 'item', 'time_spent', 'user',
                  'complete', 'correct', 'hinted', 'answer', 'simple_answer', 'interaction_history')

class ExamAttemptLogSerializer(KolibriModelSerializer):
    answer = serializers.JSONField(default='{}', allow_null=True)
    interaction_history = serializers.JSONField(default='[]')

    class Meta:
        model = ExamAttemptLog
        fields = ('id', 'examlog', 'start_timestamp', 'channel_id', 'content_id',
                  'end_timestamp', 'completion_timestamp', 'item', 'time_spent', 'user',
                  'complete', 'correct', 'hinted', 'answer', 'simple_answer', 'interaction_history')

    def validate(self, data):
        # Only do this validation when both are being set
        # not necessary on PATCH, for example
        if data.get('examlog') and data.get('user'):
            try:
                if data['examlog'].user != data['user']:
                    raise serializers.ValidationError('User field and user for related exam log are not the same')
            except ExamLog.DoesNotExist:
                raise serializers.ValidationError('Invalid exam log')
        return data

class ContentSummaryLogSerializer(KolibriModelSerializer):

    currentmasterylog = serializers.SerializerMethodField()
    extra_fields = serializers.JSONField(default='{}')

    class Meta:
        model = ContentSummaryLog
        fields = ('pk', 'user', 'content_id', 'channel_id', 'start_timestamp', 'currentmasterylog',
                  'end_timestamp', 'completion_timestamp', 'time_spent', 'progress', 'kind', 'extra_fields')

    def get_currentmasterylog(self, obj):
        try:
            current_log = obj.masterylogs.latest('end_timestamp')
            return MasteryLogSerializer(current_log).data
        except MasteryLog.DoesNotExist:
            return None

class UserSessionLogSerializer(KolibriModelSerializer):

    class Meta:
        model = UserSessionLog
        fields = ('pk', 'user', 'channels', 'start_timestamp', 'last_interaction_timestamp', 'pages')

class TotalContentProgressSerializer(serializers.ModelSerializer):

    progress = serializers.SerializerMethodField()

    class Meta:
        model = FacilityUser
        fields = ('progress', 'id')

    def get_progress(self, obj):
        return obj.contentsummarylog_set.filter(progress=1).aggregate(Sum('progress')).get('progress__sum')


class ReportsDataOfflineSerializer(serializers.ModelSerializer):
    created_by = PrimaryKeyRelatedField(read_only=False, queryset=FacilityUser.objects.all())
    modified_by = PrimaryKeyRelatedField(read_only=False, queryset=FacilityUser.objects.all())
    student_response = JSONField(default='[]')

    class Meta:
        model = ReportsDataOffline
        fields = (
            'class_id',
            'student_id',
            'number_of_attempt',
            'course_id',
            'unit_id',
            'lesson_id',
            'collection_id',
            'collection_type',
            'content_id',
            'content_type',
            'time_spent',
            'reaction',
            'student_response',
            'score',
            'created_by',
            'created_date',
            'modified_by',
            'modified_date',
            'attended',
        )

    def create(self, validated_data):
        """
        POST a new Lesson with the following payload
        {
            "title": "Lesson Title",
            "description": "Lesson Description",
            "resources": [...], // Array of {contentnode_id, channel_id, content_id}
            "is_active": false,
            "collection": "df6308209356328f726a09aa9bd323b7", // classroom ID
            "lesson_assignments": [{"collection": "df6308209356328f726a09aa9bd323b7"}] // learnergroup IDs
        }
        """
        # assignees = validated_data.pop('lesson_assignments')
        # logger.info('creating an object')
        try:
            old_report = ReportsDataOffline.objects.get(student_id=validated_data.get('student_id'),
                                                        collection_id=validated_data.get('collection_id'))
            return self.update(old_report, validated_data)
        except Exception as exp:
            new_report = ReportsDataOffline.objects.create(**validated_data)
            return new_report

    def update(self, instance, validated_data):
        # Update the scalar fields
        instance.class_id = validated_data.get('class_id', instance.class_id)
        instance.student_id = validated_data.get('student_id', instance.student_id)
        instance.number_of_attempt += 1 #validated_data.get('number_of_attempt', instance.number_of_attempt)
        instance.course_id = validated_data.get('course_id', instance.course_id)
        instance.unit_id = validated_data.get('unit_id', instance.unit_id)
        instance.lesson_id = validated_data.get('lesson_id', instance.lesson_id)
        instance.collection_id = validated_data.get('collection_id', instance.collection_id)
        instance.collection_type = validated_data.get('collection_type', instance.collection_type)
        instance.content_id = validated_data.get('content_id', instance.content_id)
        instance.content_type = validated_data.get('content_type', instance.content_type)
        instance.time_spent += validated_data.get('time_spent', 0)
        instance.reaction = validated_data.get('reaction', instance.reaction)
        instance.student_response = validated_data.get('student_response', instance.student_response)
        instance.score = validated_data.get('score', instance.score)
        instance.created_by = validated_data.get('created_by', instance.created_by)
        instance.created_date = validated_data.get('created_date', instance.created_date)
        instance.modified_by = validated_data.get('modified_by', instance.modified_by)
        instance.modified_date = validated_data.get('modified_date', instance.modified_date)
        instance.attended = validated_data.get('attended', 0)

        instance.save()
        return instance
