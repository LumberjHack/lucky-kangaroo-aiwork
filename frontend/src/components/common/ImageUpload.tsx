import React, { useState, useRef, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon, AlertCircle, Check } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface UploadedImage {
  id: string;
  file: File;
  preview: string;
  url?: string;
  isUploading: boolean;
  isUploaded: boolean;
  error?: string;
}

interface ImageUploadProps {
  onImagesChange: (images: UploadedImage[]) => void;
  maxImages?: number;
  maxSize?: number; // en MB
  acceptedTypes?: string[];
  className?: string;
  disabled?: boolean;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onImagesChange,
  maxImages = 10,
  maxSize = 5,
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
  className = '',
  disabled = false
}) => {
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Gérer l'ajout d'images
  const handleImages = useCallback((newFiles: File[]) => {
    if (disabled) return;

    const validFiles: File[] = [];
    const errors: string[] = [];

    newFiles.forEach(file => {
      // Vérifier le type de fichier
      if (!acceptedTypes.includes(file.type)) {
        errors.push(`${file.name}: Type de fichier non supporté`);
        return;
      }

      // Vérifier la taille
      if (file.size > maxSize * 1024 * 1024) {
        errors.push(`${file.name}: Fichier trop volumineux (max ${maxSize}MB)`);
        return;
      }

      // Vérifier le nombre maximum d'images
      if (images.length + validFiles.length >= maxImages) {
        errors.push(`Maximum ${maxImages} images autorisées`);
        return;
      }

      validFiles.push(file);
    });

    // Afficher les erreurs
    if (errors.length > 0) {
      errors.forEach(error => toast.error(error));
    }

    // Ajouter les nouvelles images
    const newImages: UploadedImage[] = validFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      preview: URL.createObjectURL(file),
      isUploading: false,
      isUploaded: false
    }));

    const updatedImages = [...images, ...newImages];
    setImages(updatedImages);
    onImagesChange(updatedImages);
  }, [images, maxImages, maxSize, acceptedTypes, disabled, onImagesChange]);

  // Configuration de dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleImages,
    accept: acceptedTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {} as Record<string, string[]>),
    maxSize: maxSize * 1024 * 1024,
    maxFiles: maxImages - images.length,
    disabled: disabled || images.length >= maxImages
  });

  // Supprimer une image
  const removeImage = (imageId: string) => {
    if (disabled) return;

    const updatedImages = images.filter(img => {
      if (img.id === imageId) {
        // Libérer l'URL de prévisualisation
        URL.revokeObjectURL(img.preview);
        return false;
      }
      return true;
    });

    setImages(updatedImages);
    onImagesChange(updatedImages);
  };

  // Upload d'une image
  const uploadImage = async (image: UploadedImage) => {
    const formData = new FormData();
    formData.append('image', image.file);

    try {
      setIsUploading(true);
      
      // Marquer l'image comme en cours d'upload
      setImages(prev => prev.map(img => 
        img.id === image.id 
          ? { ...img, isUploading: true, error: undefined }
          : img
      ));

      const response = await fetch('http://localhost:5000/api/listings/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'upload');
      }

      const data = await response.json();

      // Marquer l'image comme uploadée
      setImages(prev => prev.map(img => 
        img.id === image.id 
          ? { 
              ...img, 
              isUploading: false, 
              isUploaded: true, 
              url: data.url,
              error: undefined 
            }
          : img
      ));

      toast.success('Image uploadée avec succès');
    } catch (error) {
      console.error('Erreur upload:', error);
      
      // Marquer l'image avec une erreur
      setImages(prev => prev.map(img => 
        img.id === image.id 
          ? { 
              ...img, 
              isUploading: false, 
              isUploaded: false, 
              error: 'Erreur lors de l\'upload' 
            }
          : img
      ));

      toast.error('Erreur lors de l\'upload de l\'image');
    } finally {
      setIsUploading(false);
    }
  };

  // Upload de toutes les images
  const uploadAllImages = async () => {
    const imagesToUpload = images.filter(img => !img.isUploaded && !img.isUploading);
    
    for (const image of imagesToUpload) {
      await uploadImage(image);
    }
  };

  // Ouvrir le sélecteur de fichiers
  const openFileDialog = () => {
    if (disabled || images.length >= maxImages) return;
    fileInputRef.current?.click();
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Zone de drop */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${disabled || images.length >= maxImages 
            ? 'opacity-50 cursor-not-allowed' 
            : ''
          }
        `}
      >
        <input {...getInputProps()} ref={fileInputRef} />
        
        <div className="space-y-2">
          <Upload className="w-8 h-8 mx-auto text-gray-400" />
          
          {isDragActive ? (
            <p className="text-blue-600 font-medium">
              Déposez les images ici...
            </p>
          ) : (
            <div>
              <p className="text-gray-600 font-medium">
                Glissez-déposez vos images ici
              </p>
              <p className="text-sm text-gray-500">
                ou{' '}
                <button
                  type="button"
                  onClick={openFileDialog}
                  className="text-blue-600 hover:text-blue-700 underline"
                  disabled={disabled || images.length >= maxImages}
                >
                  parcourez vos fichiers
                </button>
              </p>
            </div>
          )}
          
          <p className="text-xs text-gray-400">
            {acceptedTypes.map(type => type.split('/')[1]).join(', ').toUpperCase()} • 
            Max {maxSize}MB • 
            {images.length}/{maxImages} images
          </p>
        </div>
      </div>

      {/* Liste des images */}
      {images.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">
              Images sélectionnées ({images.length})
            </h3>
            
            {images.some(img => !img.isUploaded && !img.isUploading) && (
              <button
                type="button"
                onClick={uploadAllImages}
                disabled={isUploading}
                className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {isUploading ? 'Upload...' : 'Uploader tout'}
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {images.map((image) => (
              <div
                key={image.id}
                className="relative group bg-gray-100 rounded-lg overflow-hidden aspect-square"
              >
                {/* Image */}
                <img
                  src={image.preview}
                  alt="Preview"
                  className="w-full h-full object-cover"
                />

                {/* Overlay */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity">
                  {/* Bouton supprimer */}
                  <button
                    type="button"
                    onClick={() => removeImage(image.id)}
                    disabled={disabled}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 disabled:opacity-50"
                  >
                    <X className="w-4 h-4" />
                  </button>

                  {/* Statut */}
                  <div className="absolute bottom-2 left-2 right-2">
                    {image.isUploading && (
                      <div className="flex items-center space-x-1 bg-blue-500 text-white px-2 py-1 rounded text-xs">
                        <div className="animate-spin w-3 h-3 border border-white border-t-transparent rounded-full"></div>
                        <span>Upload...</span>
                      </div>
                    )}
                    
                    {image.isUploaded && (
                      <div className="flex items-center space-x-1 bg-green-500 text-white px-2 py-1 rounded text-xs">
                        <Check className="w-3 h-3" />
                        <span>Uploadé</span>
                      </div>
                    )}
                    
                    {image.error && (
                      <div className="flex items-center space-x-1 bg-red-500 text-white px-2 py-1 rounded text-xs">
                        <AlertCircle className="w-3 h-3" />
                        <span>Erreur</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Bouton upload individuel */}
                {!image.isUploaded && !image.isUploading && (
                  <button
                    type="button"
                    onClick={() => uploadImage(image)}
                    disabled={disabled}
                    className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Upload className="w-6 h-6" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Aide */}
      <div className="text-xs text-gray-500 space-y-1">
        <p>• La première image sera utilisée comme image principale</p>
        <p>• Les images sont automatiquement redimensionnées</p>
        <p>• Formats supportés: JPG, PNG, WebP, GIF</p>
      </div>
    </div>
  );
};

export default ImageUpload;
