from django.urls import path
from . import views

urlpatterns = [
    path('', views.listado_fichas_alumnos_view, name='listado_fichas_alumnos'),
    path('agregar_ficha', views.form_agregar_ficha_alumno, name='agregar_ficha_alumno'),
    path('ficha_alumno/<str:rut>', views.ficha_alumno_view, name='ficha_alumno'),
    path('modificar_ficha/<str:rut>', views.change_ficha_alumno, name='change_ficha_alumno'),
    path('modificar_avance/<int:id>', views.change_avance_alumno, name='modificar_avance_alumno'),
    path('eliminar_avance/<int:id>', views.delete_avance_alumno, name='eliminar_avance_alumno'),
    path('eliminar_trabajo/<int:id>', views.delete_banco_trabajo, name='eliminar_trabajo_alumno'),
    path('eliminar_documento/<int:id>', views.delete_banco_documento, name='eliminar_documento_alumno'),
    path('retirar_ficha_alumno/<str:rut>', views.retirar_ficha_alumno, name='retirar_ficha_alumno'),
    path('pdf/habilidades_pragmaticas/', views.generate_doc_cotejo_hab_prag, name='generate_hab_prag'),
    path('pdf/habilidades_pragmaticas/<str:rut>', views.generate_doc_cotejo_hab_prag, name='generate_hab_prag'),
    path('pdf/anamnesis', views.generate_doc_anamnesis, name='generate_anamnesis'),
    path('pdf/anamnesis/<str:rut>', views.generate_doc_anamnesis, name='generate_anamnesis'),
    path('pdf/tecal', views.generate_doc_tecal, name='generate_tecal'),
    path('pdf/tecal/<str:rut>', views.generate_doc_tecal, name='generate_tecal'),
    path('pdf/tecal_confirmacion', views.confirmation_tecal, name="confirmation_tecal"),
    path('pdf/fonoaudiologica', views.generate_doc_fonoaudiologica, name='generate_fonoaudio'),
    path('pdf/fonoaudiologica/<str:rut>', views.generate_doc_fonoaudiologica, name='generate_fonoaudio'),
    path('pdf/teprosif', views.generate_doc_teprosif, name='generate_teprosif'),
    path('pdf/teprosif/<str:rut>', views.generate_doc_teprosif, name='generate_teprosif'),
    path('pdf/teprosif_puntajes', views.generate_doc_final_teprosif, name='teprosif_puntajes'),
    path('pdf/stsg', views.generate_doc_stsg, name='generate_stsg'),
    path('pdf/stsg/<str:rut>', views.generate_doc_stsg, name='generate_stsg'),
]
