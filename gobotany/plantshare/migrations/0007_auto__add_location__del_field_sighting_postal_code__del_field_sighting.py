# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Location'
        db.create_table('plantshare_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_input', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('plantshare', ['Location'])

        # Deleting field 'Sighting.postal_code'
        db.delete_column('plantshare_sighting', 'postal_code')

        # Deleting field 'Sighting.city'
        db.delete_column('plantshare_sighting', 'city')

        # Deleting field 'Sighting.longitude'
        db.delete_column('plantshare_sighting', 'longitude')

        # Deleting field 'Sighting.state'
        db.delete_column('plantshare_sighting', 'state')

        # Deleting field 'Sighting.latitude'
        db.delete_column('plantshare_sighting', 'latitude')

        # Adding field 'Sighting.location'
        db.add_column('plantshare_sighting', 'location',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['plantshare.Location'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Location'
        db.delete_table('plantshare_location')

        # Adding field 'Sighting.postal_code'
        db.add_column('plantshare_sighting', 'postal_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=12, blank=True),
                      keep_default=False)

        # Adding field 'Sighting.city'
        db.add_column('plantshare_sighting', 'city',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True),
                      keep_default=False)

        # Adding field 'Sighting.longitude'
        db.add_column('plantshare_sighting', 'longitude',
                      self.gf('django.db.models.fields.FloatField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Sighting.state'
        db.add_column('plantshare_sighting', 'state',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank=True),
                      keep_default=False)

        # Adding field 'Sighting.latitude'
        db.add_column('plantshare_sighting', 'latitude',
                      self.gf('django.db.models.fields.FloatField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Sighting.location'
        db.delete_column('plantshare_sighting', 'location_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'plantshare.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'user_input': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'plantshare.sharinggroup': {
            'Meta': {'object_name': 'SharingGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groups'", 'symmetrical': 'False', 'through': "orm['plantshare.SharingGroupMember']", 'to': "orm['plantshare.UserProfile']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'plantshare.sharinggroupmember': {
            'Meta': {'object_name': 'SharingGroupMember'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['plantshare.SharingGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['plantshare.UserProfile']"})
        },
        'plantshare.sighting': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Sighting'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identification': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['plantshare.Location']", 'null': 'True'}),
            'location_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'plantshare.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'saying': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'security_answer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'security_question': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'sharing_visibility': ('django.db.models.fields.CharField', [], {'default': "'PRIVATE'", 'max_length': '7'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        }
    }

    complete_apps = ['plantshare']