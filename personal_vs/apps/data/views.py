import mimetypes
import os
from pathlib import Path

from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import FileResponse, Http404

from apps.data.models import Video


class VideoListView(ListView):
    model = Video
    template_name = 'video/video_list.html'
    context_object_name = 'videos'


class VideoPlayerView(DetailView):
    model = Video
    template_name = 'video/video_player.html'
    context_object_name = 'video'


def stream_video(request, pk):
    """
    Abre o arquivo apontado por Video.file_path e devolve um FileResponse,
    permitindo que o <video> do navegador faça seek (range requests).
    """
    video = get_object_or_404(Video, pk=pk)
    file_path = video.file_path

    if not Path(file_path).exists():
        raise Http404(f"Vídeo não encontrado: {file_path}")

    # Detecta o content-type (ex: video/mp4)
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or "application/octet-stream"

    # Retorna streaming eficiente, com suporte a bytes ranges
    response = FileResponse(open(file_path, "rb"), content_type=content_type)
    response["Content-Length"] = os.path.getsize(file_path)
    response["Accept-Ranges"] = "bytes"
    return response