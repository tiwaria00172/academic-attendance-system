import React, { useRef } from 'react';
import { Upload, X, ImagePlus } from 'lucide-react';

export default function PhotoUpload({ photos, onChange }) {
  const inputRef = useRef(null);

  const addFiles = (files) => {
    const imgs = Array.from(files).filter((f) => f.type.startsWith('image/'));
    const combined = [...photos, ...imgs].slice(0, 4);
    onChange(combined);
  };

  const remove = (idx) => onChange(photos.filter((_, i) => i !== idx));

  const handleDrop = (e) => { e.preventDefault(); addFiles(e.dataTransfer.files); };
  const handleDragOver = (e) => e.preventDefault();

  return (
    <div>
      {/* Drop zone */}
      <div onDrop={handleDrop} onDragOver={handleDragOver}
           onClick={() => inputRef.current?.click()}
           className="border-2 border-dashed border-slate-300 rounded-2xl p-10
                      text-center cursor-pointer transition-all duration-200
                      hover:border-brand-400 hover:bg-brand-50/30 group">
        <div className="w-14 h-14 rounded-2xl bg-brand-50 flex items-center justify-center
                        mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
          <ImagePlus size={28} className="text-brand-500" />
        </div>
        <p className="text-lg font-semibold text-slate-700 mb-1">
          Drop class photos here
        </p>
        <p className="text-sm text-slate-400">
          JPG or PNG · Max 4 photos · Click to browse
        </p>
        <input ref={inputRef} type="file" multiple accept="image/*"
               onChange={(e) => addFiles(e.target.files)} className="hidden" />
      </div>

      {/* Previews */}
      {photos.length > 0 && (
        <div className="mt-5">
          <p className="text-sm font-medium text-slate-600 mb-3">
            Selected ({photos.length}/4)
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {photos.map((file, i) => (
              <div key={i} className="relative group rounded-xl overflow-hidden
                                      ring-1 ring-slate-200 aspect-[4/3]">
                <img src={URL.createObjectURL(file)} alt=""
                     className="w-full h-full object-cover" />
                <button onClick={(e) => { e.stopPropagation(); remove(i); }}
                        className="absolute top-1.5 right-1.5 w-7 h-7 rounded-full
                                   bg-black/50 backdrop-blur text-white
                                   flex items-center justify-center
                                   opacity-0 group-hover:opacity-100 transition-opacity">
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
