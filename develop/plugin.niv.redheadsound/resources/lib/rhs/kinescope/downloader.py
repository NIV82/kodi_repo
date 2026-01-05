# Импорт необходимых модулей стандартной библиотеки
import sys
from io import BytesIO
from os import PathLike
from typing import Union
from pathlib import Path
from requests import Session
from subprocess import Popen
from shutil import copyfileobj, rmtree
from base64 import b64decode, b64encode
from requests.exceptions import ChunkedEncodingError
from tqdm import tqdm  # Для отображения прогресс-бара

# Импорт сторонних библиотек для работы с MPD (Media Presentation Description)
from mpegdash.parser import MPEGDASHParser, MPEGDASH

# Импорт внутренних модулей проекта
from kinescope.kinescope import KinescopeVideo
from kinescope.const import KINESCOPE_BASE_URL
from kinescope.exceptions import *


class VideoDownloader:
    def __init__(self, kinescope_video: KinescopeVideo,
                 temp_dir: Union[str, PathLike] = str(Path(__file__).parent / 'temp'),
                 ffmpeg_path: Union[str, PathLike] = str(Path(__file__).parent / 'ffmpeg'),
                 mp4decrypt_path: Union[str, PathLike] = str(Path(__file__).parent / 'mp4decrypt')):
        """
        Инициализация загрузчика видео.
        
        Args:
            kinescope_video: Объект видео Kinescope для загрузки
            temp_dir: Путь к временной директории (по умолчанию рядом со скриптом)
            ffmpeg_path: Путь к исполняемому файлу ffmpeg
            mp4decrypt_path: Путь к исполняемому файлу mp4decrypt
        """
        self.kinescope_video: KinescopeVideo = kinescope_video
        self.temp_path: Path = Path(temp_dir)
        self.temp_path.mkdir(parents=True, exist_ok=True)  # Создаем временную директорию
        
        # Обработка путей для собранных приложений (PyInstaller)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            meipass_path = Path(sys._MEIPASS).resolve()
            self.ffmpeg_path = meipass_path / 'ffmpeg'
            self.mp4decrypt_path = meipass_path / 'mp4decrypt'
        else:
            self.ffmpeg_path = ffmpeg_path
            self.mp4decrypt_path = mp4decrypt_path
            
        self.http = Session()  # HTTP-сессия для запросов
        self.mpd_master: MPEGDASH = self._fetch_mpd_master()  # Загружаем MPD манифест

    def __del__(self):
        """Деструктор - очищаем временные файлы при удалении объекта"""
        rmtree(self.temp_path)

    def _merge_tracks(self, source_video_filepath: str | PathLike,
                      source_audio_filepath: str | PathLike,
                      target_filepath: str | PathLike):
        """
        Объединяет видео и аудио дорожки с помощью ffmpeg.
        
        Args:
            source_video_filepath: Путь к видеофайлу
            source_audio_filepath: Путь к аудиофайлу
            target_filepath: Путь для сохранения результата
        """
        try:
            Popen((self.ffmpeg_path,
                   "-i", source_video_filepath,
                   "-i", source_audio_filepath,
                   "-c", "copy", target_filepath,
                   "-y", "-loglevel", "error")).communicate()
        except FileNotFoundError:
            raise FFmpegNotFoundError('FFmpeg binary was not found at the specified path')

    def _decrypt_video(self, source_filepath: str | PathLike,
                       target_filepath: str | PathLike,
                       key: str):
        """
        Дешифрует видео с помощью mp4decrypt.
        
        Args:
            source_filepath: Путь к зашифрованному файлу
            target_filepath: Путь для сохранения расшифрованного файла
            key: Ключ дешифровки
        """
        try:
            Popen((self.mp4decrypt_path,
                   "--key", f"1:{key}",
                   source_filepath,
                   target_filepath)).communicate()
        except FileNotFoundError:
            raise FFmpegNotFoundError('mp4decrypt binary was not found at the specified path')

    def _get_license_key(self) -> str:
        """
        Получает ключ дешифровки с сервера лицензий Kinescope.
        
        Returns:
            Ключ дешифровки в hex-формате или None, если видео не зашифровано
            
        Raises:
            UnsupportedEncryption: Если используется неподдерживаемый тип шифрования
        """
        try:
            return b64decode(
                self.http.post(
                    url=self.kinescope_video.get_clearkey_license_url(),
                    headers={'origin': KINESCOPE_BASE_URL},
                    json={
                        'kids': [
                            b64encode(bytes.fromhex(
                                self.mpd_master
                                .periods[0]
                                .adaptation_sets[0]
                                .content_protections[0]
                                .cenc_default_kid.replace('-', '')
                            )).decode().replace('=', '')
                        ],
                        'type': 'temporary'
                    }
                ).json()['keys'][0]['k'] + '=='
            ).hex() if self.mpd_master.periods[0].adaptation_sets[0].content_protections else None
        except KeyError:
            raise UnsupportedEncryption(
                "Unfortunately, only the ClearKey encryption type is currently supported, "
                "but not the one in this video"
            )

    def _fetch_segment(self,
                       segment_url: str,
                       file):
        """
        Загружает один сегмент видео с повторными попытками при ошибках.
        
        Args:
            segment_url: URL сегмента для загрузки
            file: Файловый объект для сохранения
            
        Raises:
            SegmentDownloadError: Если не удалось загрузить сегмент после 5 попыток
        """
        for _ in range(5):
            try:
                copyfileobj(
                    BytesIO(self.http.get(segment_url, stream=True).content),
                    file
                )
                return
            except ChunkedEncodingError:
                pass
        raise SegmentDownloadError(f'Failed to download segment {segment_url}')

    def _fetch_segments(self,
                        segments_urls: list[str],
                        filepath: str | PathLike,
                        progress_bar_label: str = ''):
        """
        Загружает все сегменты с отображением прогресса.
        
        Args:
            segments_urls: Список URL сегментов
            filepath: Путь для сохранения объединенного файла
            progress_bar_label: Метка для прогресс-бара
        """
        segments_urls = [seg for i, seg in enumerate(segments_urls) if i == segments_urls.index(seg)]
        with open(filepath, 'wb') as f:
            with tqdm(desc=progress_bar_label,
                      total=len(segments_urls),
                      bar_format='{desc}: {percentage:3.0f}%|{bar:10}| [{n_fmt}/{total_fmt}]') as progress_bar:
                for segment_url in segments_urls:
                    self._fetch_segment(segment_url, f)
                    progress_bar.update()

    def _get_segments_urls(self, resolution: tuple[int, int]) -> dict[str:list[str]]:
        """
        Получает URL сегментов для заданного разрешения.
        
        Args:
            resolution: Кортеж (ширина, высота) требуемого разрешения
            
        Returns:
            Словарь с ключами 'video/mp4' и 'audio/mp4', содержащими списки URL
            
        Raises:
            InvalidResolution: Если запрошено несуществующее разрешение
        """
        try:
            result = {}
            for adaptation_set in self.mpd_master.periods[0].adaptation_sets:
                resolutions = [(r.width, r.height) for r in adaptation_set.representations]
                idx = resolutions.index(resolution) if adaptation_set.representations[0].height else 0
                representation = adaptation_set.representations[idx]
                base_url = representation.base_urls[0].base_url_value
                result[adaptation_set.mime_type] = [
                    base_url + (segment_url.media or '') 
                    for segment_url in representation.segment_lists[0].segment_urls]

            return result
        except ValueError:
            raise InvalidResolution('Invalid resolution specified')

    def _fetch_mpd_master(self) -> MPEGDASH:
        """Загружает и парсит MPD манифест видео."""
        return MPEGDASHParser.parse(self.http.get(
            url=self.kinescope_video.get_mpd_master_playlist_url(),
            headers={'Referer': KINESCOPE_BASE_URL}
        ).text)

    def get_resolutions(self) -> list[tuple[int, int]]:
        """
        Возвращает список доступных разрешений видео.
        
        Returns:
            Список кортежей (ширина, высота), отсортированный по высоте
        """
        for adaptation_set in self.mpd_master.periods[0].adaptation_sets:
            if adaptation_set.representations[0].height:
                return [(r.width, r.height) for r in sorted(adaptation_set.representations, key=lambda r: r.height)]

    def download(self, filepath: str, resolution: tuple[int, int] = None):
        """
        Основной метод для загрузки видео.
        
        Args:
            filepath: Путь для сохранения итогового файла
            resolution: Желаемое разрешение (если None - максимальное доступное)
        """
        if not resolution:
            resolution = self.get_resolutions()[-1]  # Берем максимальное разрешение
            
        key = self._get_license_key()  # Получаем ключ дешифровки (если есть)
        
        # Загрузка видео дорожки
        self._fetch_segments(
            self._get_segments_urls(resolution)['video/mp4'],
            self.temp_path / f'{self.kinescope_video.video_id}_video.mp4{".enc" if key else ""}',
            'Video'
        )
        
        # Загрузка аудио дорожки
        self._fetch_segments(
            self._get_segments_urls(resolution)['audio/mp4'],
            self.temp_path / f'{self.kinescope_video.video_id}_audio.mp4{".enc" if key else ""}',
            'Audio'
        )
        
        # Дешифровка при необходимости
        if key:
            print('[*] Decrypting...', end=' ')
            self._decrypt_video(
                self.temp_path / f'{self.kinescope_video.video_id}_video.mp4.enc',
                self.temp_path / f'{self.kinescope_video.video_id}_video.mp4',
                key
            )
            self._decrypt_video(
                self.temp_path / f'{self.kinescope_video.video_id}_audio.mp4.enc',
                self.temp_path / f'{self.kinescope_video.video_id}_audio.mp4',
                key
            )
            print('Done')
            
        # Подготовка конечного файла
        filepath = Path(filepath).with_suffix('.mp4')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Объединение дорожек
        print('[*] Merging tracks...', end=' ')
        self._merge_tracks(
            self.temp_path / f'{self.kinescope_video.video_id}_video.mp4',
            self.temp_path / f'{self.kinescope_video.video_id}_audio.mp4',
            filepath
        )
        print('Done')
