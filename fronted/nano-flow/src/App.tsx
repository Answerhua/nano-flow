import React, { useState } from 'react';
import { Sparkles, Plus, Trash2, Download, RefreshCw, Wand2, AlertCircle, RotateCcw, Dices } from 'lucide-react';
import { 
  createGenerationTask, 
  createVSGenerationTask,
  pollTaskUntilComplete,
  generateSteps
} from './services/api';
import type { TaskResponse, GenerateRequest, GenerateVSRequest, GenerateResponse } from './services/api';

interface Step {
  id: number;
  title: string;
  desc: string;
}

interface VSModeData {
  mainTitle: string;
  leftScenario: {
    title: string;
    description: string;
  };
  rightScenario: {
    title: string;
    description: string;
  };
  actions: string[];
}

type Mode = 'flow' | 'vs';

// Flow Mode 预览组件
const FlowModePreview: React.FC<any> = ({
  isGenerating, hasResult, generatedImageUrl, title, error, setError,
  loadingText, progress, handleGenerate
}) => {
  return (
    <div className="h-full min-h-[500px] bg-white rounded-3xl p-2 border-4 border-white shadow-xl shadow-pink-50 flex flex-col">
      <div className="flex-1 bg-slate-50 rounded-2xl flex flex-col items-center justify-center overflow-hidden relative group">
        
        {/* Empty State */}
        {!isGenerating && !hasResult && !error && (
          <div className="text-center p-8">
            <div className="w-32 h-32 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-6 text-4xl animate-bounce-slow">
              🎨
            </div>
            <h3 className="text-xl font-bold text-slate-700 mb-2">等待灵感注入</h3>
            <p className="text-slate-400 max-w-xs mx-auto">在左侧输入你的想法，AI 将为你生成可爱的 Nano Banana 风格信息图。</p>
          </div>
        )}

        {/* Loading State */}
        {isGenerating && (
          <div className="text-center z-10">
            <div className="w-20 h-20 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin mx-auto mb-6"></div>
            <p className="text-lg font-medium text-slate-600 animate-pulse mb-3">{loadingText}</p>
            {progress > 0 && (
              <div className="max-w-xs mx-auto">
                <div className="bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-pink-400 to-orange-400 h-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-slate-400 mt-2">{progress}%</p>
              </div>
            )}
          </div>
        )}

        {/* Result - 显示生成的图片 */}
        {hasResult && generatedImageUrl && (
          <div className="relative w-full h-full flex flex-col items-center justify-center p-4 animate-fade-in">
            <img 
              src={generatedImageUrl} 
              alt={title}
              className="max-w-full max-h-full object-contain rounded-xl shadow-lg"
              onError={() => {
                console.error('Image load error');
                setError('图片加载失败');
              }}
            />
          </div>
        )}

        {/* Error State */}
        {error && !isGenerating && (
          <div className="text-center p-8">
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="text-red-500" size={40} />
            </div>
            <h3 className="text-xl font-bold text-slate-700 mb-2">出错了</h3>
            <p className="text-red-500 max-w-xs mx-auto mb-4">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="px-6 py-2 bg-slate-200 hover:bg-slate-300 rounded-xl transition-colors"
            >
              关闭
            </button>
          </div>
        )}
      </div>

      {/* Action Bar */}
      {hasResult && generatedImageUrl && (
        <div className="p-4 flex gap-3 justify-end">
          <button 
            onClick={handleGenerate}
            className="flex items-center px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors text-sm font-bold"
          >
            <RefreshCw size={16} className="mr-2" /> Regenerate
          </button>
          <a 
            href={generatedImageUrl}
            download={`${title.replace(/\s+/g, '_')}_nano_flow.png`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center px-6 py-2 bg-slate-800 text-white hover:bg-slate-700 rounded-xl transition-colors text-sm font-bold shadow-lg shadow-slate-200"
          >
            <Download size={16} className="mr-2" /> Download
          </a>
        </div>
      )}
    </div>
  );
};

// VS Mode 预览组件
const VSModePreview: React.FC<any> = ({
  isGenerating, hasResult, generatedImageUrl, vsModeData, error, setError,
  loadingText, progress, handleGenerate
}) => {
  return (
    <div className="h-full min-h-[500px] bg-white rounded-3xl p-2 border-4 border-white shadow-xl shadow-blue-50 flex flex-col">
      <div className="flex-1 bg-slate-50 rounded-2xl overflow-hidden relative">
        
        {/* Empty State */}
        {!isGenerating && !hasResult && !error && (
          <div className="h-full flex flex-col items-center justify-center text-center p-8">
            <div className="w-32 h-32 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 text-4xl animate-bounce-slow">
              ⚡
            </div>
            <h3 className="text-xl font-bold text-slate-700 mb-2">等待对比内容</h3>
            <p className="text-slate-400 max-w-xs mx-auto">在左侧输入对比场景，AI 将为你生成左右对比的可爱风格图。</p>
          </div>
        )}

        {/* Loading State */}
        {isGenerating && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center z-10">
              <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-6"></div>
              <p className="text-lg font-medium text-slate-600 animate-pulse mb-3">{loadingText}</p>
              {progress > 0 && (
                <div className="max-w-xs mx-auto">
                  <div className="bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-blue-400 to-purple-400 h-full transition-all duration-500"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-slate-400 mt-2">{progress}%</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Preview - 未生成时显示预览布局 */}
        {!isGenerating && !hasResult && !error && (vsModeData.leftScenario.title || vsModeData.rightScenario.title) && (
          <div className="h-full flex flex-col p-6 animate-fade-in">
            {/* Main Title - Auto Generated */}
            <h2 className="text-2xl font-bold text-center text-slate-700 mb-6">
              {(() => {
                const leftTitle = vsModeData.leftScenario.title.trim();
                const rightTitle = vsModeData.rightScenario.title.trim();
                if (leftTitle && rightTitle) {
                  return `${leftTitle} vs ${rightTitle}`;
                } else if (leftTitle) {
                  return `${leftTitle} VS`;
                } else if (rightTitle) {
                  return `VS ${rightTitle}`;
                } else {
                  return 'VS';
                }
              })()}
            </h2>
            
            {/* VS Layout */}
            <div className="flex-1 flex gap-4">
              {/* Left Side (Bad/Negative) */}
              <div className="flex-1 bg-red-50 border-2 border-red-200 rounded-2xl p-4 flex flex-col">
                <div className="text-center mb-4">
                  <span className="text-4xl mb-2 block">😰</span>
                  <h3 className="font-bold text-red-600 text-lg">{vsModeData.leftScenario.title || '左侧场景'}</h3>
                </div>
                <p className="text-sm text-slate-600 flex-1 overflow-auto">
                  {vsModeData.leftScenario.description || '描述内容将显示在这里...'}
                </p>
              </div>

              {/* VS Divider */}
              <div className="flex items-center justify-center">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-red-400 to-green-400 flex items-center justify-center text-white font-bold shadow-lg">
                  VS
                </div>
              </div>

              {/* Right Side (Good/Positive) */}
              <div className="flex-1 bg-green-50 border-2 border-green-200 rounded-2xl p-4 flex flex-col">
                <div className="text-center mb-4">
                  <span className="text-4xl mb-2 block">😊</span>
                  <h3 className="font-bold text-green-600 text-lg">{vsModeData.rightScenario.title || '右侧场景'}</h3>
                </div>
                <p className="text-sm text-slate-600 flex-1 overflow-auto">
                  {vsModeData.rightScenario.description || '描述内容将显示在这里...'}
                </p>
              </div>
            </div>

            {/* Actions Bar */}
            {vsModeData.actions.some((a: string) => a.trim()) && (
              <div className="mt-4 flex gap-2 justify-center flex-wrap">
                {vsModeData.actions.filter((a: string) => a.trim()).map((action: string, idx: number) => (
                  <div 
                    key={idx}
                    className="px-4 py-2 bg-blue-100 text-blue-600 rounded-full text-sm font-bold border-2 border-blue-200"
                  >
                    💡 {action}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Result - 显示生成的图片 */}
        {hasResult && generatedImageUrl && (
          <div className="h-full flex items-center justify-center p-4 animate-fade-in">
            <img 
              src={generatedImageUrl} 
              alt={(() => {
                const leftTitle = vsModeData.leftScenario.title.trim();
                const rightTitle = vsModeData.rightScenario.title.trim();
                if (leftTitle && rightTitle) return `${leftTitle} vs ${rightTitle}`;
                if (leftTitle) return `${leftTitle} VS`;
                if (rightTitle) return `VS ${rightTitle}`;
                return 'VS';
              })()}
              className="max-w-full max-h-full object-contain rounded-xl shadow-lg"
              onError={() => {
                console.error('Image load error');
                setError('图片加载失败');
              }}
            />
          </div>
        )}

        {/* Error State */}
        {error && !isGenerating && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center p-8">
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <AlertCircle className="text-red-500" size={40} />
              </div>
              <h3 className="text-xl font-bold text-slate-700 mb-2">出错了</h3>
              <p className="text-red-500 max-w-xs mx-auto mb-4">{error}</p>
              <button 
                onClick={() => setError(null)}
                className="px-6 py-2 bg-slate-200 hover:bg-slate-300 rounded-xl transition-colors"
              >
                关闭
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Action Bar */}
      {hasResult && generatedImageUrl && (
        <div className="p-4 flex gap-3 justify-end">
          <button 
            onClick={handleGenerate}
            className="flex items-center px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors text-sm font-bold"
          >
            <RefreshCw size={16} className="mr-2" /> Regenerate
          </button>
          <a 
            href={generatedImageUrl}
            download={`${(() => {
              const leftTitle = vsModeData.leftScenario.title.trim();
              const rightTitle = vsModeData.rightScenario.title.trim();
              let filename = 'VS';
              if (leftTitle && rightTitle) filename = `${leftTitle}_vs_${rightTitle}`;
              else if (leftTitle) filename = `${leftTitle}_VS`;
              else if (rightTitle) filename = `VS_${rightTitle}`;
              return filename.replace(/\s+/g, '_');
            })()}_vs_mode.png`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center px-6 py-2 bg-slate-800 text-white hover:bg-slate-700 rounded-xl transition-colors text-sm font-bold shadow-lg shadow-slate-200"
          >
            <Download size={16} className="mr-2" /> Download
          </a>
        </div>
      )}
    </div>
  );
};

// Flow Mode 输入面板组件
const FlowModeInputPanel: React.FC<any> = ({
  title, setTitle, steps, setSteps, selectedCharacter, setSelectedCharacter,
  isGeneratingSteps, handleSmartFill, handleClear, hasContent, addStep, removeStep,
  handleGenerate, isGenerating
}) => {
  return (
    <div className="lg:col-span-5 space-y-6">
      <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl shadow-pink-100 border border-white">
        
        {/* Title Input */}
        <div className="mb-6">
          <label className="block text-sm font-bold text-slate-400 mb-2 uppercase tracking-wider">Project Title</label>
          <div className="flex gap-2">
            <input 
              type="text" 
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="例如: 如何制作美味拿铁"
              className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl px-4 py-3 focus:outline-none focus:border-pink-300 transition-colors"
            />
            <button 
              onClick={handleSmartFill}
              disabled={isGeneratingSteps}
              className={`p-3 rounded-2xl transition-colors relative ${
                isGeneratingSteps
                  ? 'bg-blue-100 text-blue-300 cursor-wait'
                  : 'bg-blue-50 text-blue-400 hover:bg-blue-100'
              }`}
              title={title.trim() ? '根据标题生成步骤' : '生成示例'}
            >
              {isGeneratingSteps ? (
                <div className="w-5 h-5 border-2 border-blue-300 border-t-blue-500 rounded-full animate-spin"></div>
              ) : title.trim() ? (
                <Wand2 size={20} />
              ) : (
                <Dices size={20} />
              )}
            </button>
            {hasContent() && (
              <button 
                onClick={handleClear}
                className="p-3 text-slate-300 hover:text-red-500 rounded-2xl hover:bg-red-50 transition-colors"
                title="清空所有内容"
              >
                <RotateCcw size={20} />
              </button>
            )}
          </div>
        </div>

        {/* Steps Timeline */}
        <div className="space-y-4 mb-8">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-bold text-slate-400 uppercase tracking-wider">Flow Steps</label>
            <span className="text-xs text-pink-400 bg-pink-50 px-2 py-1 rounded-full">{steps.length} Steps</span>
          </div>
          
          <div className="relative pl-4 border-l-2 border-dashed border-slate-200 space-y-6">
            {steps.map((step: Step, index: number) => (
              <div key={step.id} className="relative group">
                <div className="absolute -left-[21px] top-3 w-3 h-3 rounded-full bg-pink-300 ring-4 ring-pink-50"></div>
                <div className="bg-white border border-slate-100 rounded-2xl p-3 shadow-sm group-hover:shadow-md transition-shadow relative">
                  <div className="flex justify-between mb-2">
                    <input 
                      className="font-bold text-slate-700 bg-transparent focus:outline-none w-full"
                      value={step.title}
                      onChange={(e) => {
                        const newSteps = [...steps];
                        newSteps[index].title = e.target.value;
                        setSteps(newSteps);
                      }}
                    />
                    <button onClick={() => removeStep(step.id)} className="text-slate-300 hover:text-red-400 transition-colors">
                      <Trash2 size={16} />
                    </button>
                  </div>
                  <textarea 
                    className="w-full text-sm text-slate-500 bg-slate-50 rounded-xl p-2 focus:outline-none resize-none"
                    rows={2}
                    placeholder="描述这一步图片中人物在做什么..."
                    value={step.desc}
                    onChange={(e) => {
                      const newSteps = [...steps];
                      newSteps[index].desc = e.target.value;
                      setSteps(newSteps);
                    }}
                  />
                </div>
              </div>
            ))}
            
            {/* Add Step Button */}
            <button 
              onClick={addStep}
              className="relative flex items-center text-sm font-bold text-slate-400 hover:text-pink-500 transition-colors ml-2"
            >
              <Plus size={16} className="mr-1" /> Add Step
            </button>
          </div>
        </div>

        {/* Character Selection */}
        <div className="mb-6">
          <label className="block text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">
            选择主角 (Choose Character)
          </label>
          <div className="flex gap-3 justify-center">
            {/* Bear Option */}
            <button
              onClick={() => setSelectedCharacter('bear')}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all duration-300 ${
                selectedCharacter === 'bear'
                  ? 'bg-pink-50 border-pink-300 shadow-lg shadow-pink-200 scale-105'
                  : 'bg-white border-slate-200 hover:border-pink-200 hover:shadow-md'
              }`}
            >
              <svg 
                width="40" 
                height="40" 
                viewBox="0 0 48 48" 
                fill="none" 
                className={`transition-transform ${selectedCharacter === 'bear' ? 'scale-110' : ''}`}
              >
                <circle cx="14" cy="12" r="8" fill="#FFB8B8" />
                <circle cx="34" cy="12" r="8" fill="#FFB8B8" />
                <circle cx="24" cy="26" r="16" fill="#FFCACA" />
                <circle cx="19" cy="24" r="2.5" fill="#8B4513" />
                <circle cx="29" cy="24" r="2.5" fill="#8B4513" />
                <path d="M24 28 Q24 32 24 32" stroke="#8B4513" strokeWidth="2" strokeLinecap="round" />
                <path d="M21 32 Q24 34 27 32" stroke="#FF9999" strokeWidth="2" strokeLinecap="round" fill="none" />
              </svg>
              <span className={`text-sm font-bold ${selectedCharacter === 'bear' ? 'text-pink-500' : 'text-slate-500'}`}>
                小熊 Bear
              </span>
            </button>

            {/* Rabbit Option */}
            <button
              onClick={() => setSelectedCharacter('rabbit')}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all duration-300 ${
                selectedCharacter === 'rabbit'
                  ? 'bg-pink-50 border-pink-300 shadow-lg shadow-pink-200 scale-105'
                  : 'bg-white border-slate-200 hover:border-pink-200 hover:shadow-md'
              }`}
            >
              <svg 
                width="40" 
                height="40" 
                viewBox="0 0 48 48" 
                fill="none"
                className={`transition-transform ${selectedCharacter === 'rabbit' ? 'scale-110' : ''}`}
              >
                <ellipse cx="16" cy="12" rx="5" ry="14" fill="#FFE4E4" />
                <ellipse cx="32" cy="12" rx="5" ry="14" fill="#FFE4E4" />
                <ellipse cx="16" cy="12" rx="2.5" ry="10" fill="#FFC9C9" />
                <ellipse cx="32" cy="12" rx="2.5" ry="10" fill="#FFC9C9" />
                <circle cx="24" cy="28" r="14" fill="#FFF0F0" />
                <circle cx="20" cy="26" r="2" fill="#8B4513" />
                <circle cx="28" cy="26" r="2" fill="#8B4513" />
                <circle cx="24" cy="30" r="1.5" fill="#FFB8D0" />
                <path d="M21 33 Q24 35 27 33" stroke="#FFB8D0" strokeWidth="1.5" strokeLinecap="round" fill="none" />
              </svg>
              <span className={`text-sm font-bold ${selectedCharacter === 'rabbit' ? 'text-pink-500' : 'text-slate-500'}`}>
                兔子 Rabbit
              </span>
            </button>

            {/* Cat Option */}
            <button
              onClick={() => setSelectedCharacter('cat')}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all duration-300 ${
                selectedCharacter === 'cat'
                  ? 'bg-pink-50 border-pink-300 shadow-lg shadow-pink-200 scale-105'
                  : 'bg-white border-slate-200 hover:border-pink-200 hover:shadow-md'
              }`}
            >
              <svg 
                width="40" 
                height="40" 
                viewBox="0 0 48 48" 
                fill="none"
                className={`transition-transform ${selectedCharacter === 'cat' ? 'scale-110' : ''}`}
              >
                <path d="M12 20 L8 8 L16 16 Z" fill="#FFD5B8" />
                <path d="M36 20 L40 8 L32 16 Z" fill="#FFD5B8" />
                <circle cx="24" cy="26" r="15" fill="#FFE0C8" />
                <circle cx="19" cy="24" r="2.5" fill="#8B4513" />
                <circle cx="29" cy="24" r="2.5" fill="#8B4513" />
                <circle cx="24" cy="29" r="1.5" fill="#FFB8B8" />
                <path d="M24 29 L24 32" stroke="#8B4513" strokeWidth="1.5" strokeLinecap="round" />
                <path d="M20 32 Q24 34 28 32" stroke="#FFB8B8" strokeWidth="2" strokeLinecap="round" fill="none" />
                <path d="M16 26 Q12 26 10 24" stroke="#D4A574" strokeWidth="1.5" strokeLinecap="round" />
                <path d="M32 26 Q36 26 38 24" stroke="#D4A574" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              <span className={`text-sm font-bold ${selectedCharacter === 'cat' ? 'text-pink-500' : 'text-slate-500'}`}>
                小猫 Cat
              </span>
            </button>
          </div>
        </div>

        {/* Generate Button */}
        <button 
          onClick={handleGenerate}
          disabled={isGenerating || !title}
          className={`w-full py-4 rounded-2xl font-bold text-white text-lg shadow-lg shadow-pink-200 flex items-center justify-center transition-all transform hover:scale-[1.02] active:scale-[0.98]
            ${!title ? 'bg-slate-300 cursor-not-allowed' : 'bg-gradient-to-r from-pink-400 to-orange-400 hover:shadow-pink-300'}
          `}
        >
          {isGenerating ? (
            <span className="animate-pulse">Generating...</span>
          ) : (
            <>
              <Sparkles className="mr-2" /> Generate Vibe Image
            </>
          )}
        </button>
      </div>
    </div>
  );
};

// VS Mode 输入面板组件
const VSModeInputPanel: React.FC<any> = ({
  vsModeData, setVsModeData, actionCount, updateActionCount,
  handleClear, hasContent, handleGenerate, isGenerating,
  selectedCharacter, setSelectedCharacter
}) => {
  // 填充负面示例
  const fillNegativeExample = () => {
    setVsModeData({
      ...vsModeData,
      leftScenario: {
        title: '不健康生活',
        description: '熬夜、久坐、外卖、缺乏运动'
      }
    });
  };

  // 填充正面示例
  const fillPositiveExample = () => {
    setVsModeData({
      ...vsModeData,
      rightScenario: {
        title: '健康生活',
        description: '规律作息、均衡饮食、运动、精力充沛'
      },
      actions: ['早睡早起', '健康饮食', '规律运动', '保持心态']
    });
  };

  return (
    <div className="lg:col-span-5 space-y-6">
      <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl shadow-blue-100 border border-white">
        
        {/* Clear Button - moved to top right if there's content */}
        {hasContent() && (
          <div className="flex justify-end mb-4">
            <button 
              onClick={handleClear}
              className="p-2 text-slate-300 hover:text-red-500 rounded-2xl hover:bg-red-50 transition-colors"
              title="清空所有内容"
            >
              <RotateCcw size={20} />
            </button>
          </div>
        )}

        {/* Left Scenario (Negative/Bad) */}
        <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-bold text-red-600 uppercase tracking-wider">
              ❌ 负面、消极 (Negative)
            </label>
            <button 
              onClick={fillNegativeExample}
              className="p-2 bg-red-100 text-red-400 hover:bg-red-200 rounded-xl transition-colors"
              title="填充示例"
            >
              <Dices size={18} />
            </button>
          </div>
          <input 
            type="text" 
            value={vsModeData.leftScenario.title}
            onChange={(e) => setVsModeData({
              ...vsModeData,
              leftScenario: { ...vsModeData.leftScenario, title: e.target.value }
            })}
            placeholder="例如: 不好的学习方法"
            className="w-full bg-white border-2 border-red-100 rounded-xl px-4 py-3 mb-3 focus:outline-none focus:border-red-300 transition-colors"
          />
          <textarea 
            value={vsModeData.leftScenario.description}
            onChange={(e) => setVsModeData({
              ...vsModeData,
              leftScenario: { ...vsModeData.leftScenario, description: e.target.value }
            })}
            placeholder="描述图片中场景、痛点..."
            rows={4}
            className="w-full bg-white border-2 border-red-100 rounded-xl px-4 py-3 focus:outline-none focus:border-red-300 transition-colors resize-none"
          />
        </div>

        {/* Right Scenario (Positive/Good) */}
        <div className="mb-6 bg-green-50 border-2 border-green-200 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-bold text-green-600 uppercase tracking-wider">
              ✅ 正确、积极 (Positive)
            </label>
            <button 
              onClick={fillPositiveExample}
              className="p-2 bg-green-100 text-green-400 hover:bg-green-200 rounded-xl transition-colors"
              title="填充示例"
            >
              <Dices size={18} />
            </button>
          </div>
          <input 
            type="text" 
            value={vsModeData.rightScenario.title}
            onChange={(e) => setVsModeData({
              ...vsModeData,
              rightScenario: { ...vsModeData.rightScenario, title: e.target.value }
            })}
            placeholder="例如: 好的学习方法"
            className="w-full bg-white border-2 border-green-100 rounded-xl px-4 py-3 mb-3 focus:outline-none focus:border-green-300 transition-colors"
          />
          <textarea 
            value={vsModeData.rightScenario.description}
            onChange={(e) => setVsModeData({
              ...vsModeData,
              rightScenario: { ...vsModeData.rightScenario, description: e.target.value }
            })}
            placeholder="描述图片中场景、优势..."
            rows={4}
            className="w-full bg-white border-2 border-green-100 rounded-xl px-4 py-3 focus:outline-none focus:border-green-300 transition-colors resize-none"
          />
        </div>

        {/* Bottom Action Bar */}
        <div className="mb-6 bg-blue-50 border-2 border-blue-200 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-bold text-blue-600 uppercase tracking-wider">
              💡 正确做法 (Actions)
            </label>
            <div className="flex gap-2 items-center">
              <span className="text-xs text-slate-500">数量:</span>
              {[2, 3, 4].map(count => (
                <button
                  key={count}
                  onClick={() => updateActionCount(count)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                    actionCount === count
                      ? 'bg-blue-500 text-white'
                      : 'bg-white text-slate-400 hover:bg-blue-100'
                  }`}
                >
                  {count}
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {vsModeData.actions.slice(0, actionCount).map((action: string, index: number) => (
              <input
                key={index}
                type="text"
                value={action}
                onChange={(e) => {
                  const newActions = [...vsModeData.actions];
                  newActions[index] = e.target.value;
                  setVsModeData({ ...vsModeData, actions: newActions });
                }}
                placeholder={`做法 ${index + 1}`}
                className="bg-white border-2 border-blue-100 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-300 transition-colors"
              />
            ))}
          </div>
        </div>

        {/* Character Selection */}
        <div className="mb-6">
          <label className="block text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">
            选择主角 (Choose Character)
          </label>
          <div className="flex gap-3 justify-center">
            {/* Bear Option */}
            <button
              onClick={() => setSelectedCharacter('bear')}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all duration-300 ${
                selectedCharacter === 'bear'
                  ? 'bg-pink-50 border-pink-300 shadow-lg shadow-pink-200 scale-105'
                  : 'bg-white border-slate-200 hover:border-pink-200 hover:shadow-md'
              }`}
            >
              <svg 
                width="40" 
                height="40" 
                viewBox="0 0 48 48" 
                fill="none" 
                className={`transition-transform ${selectedCharacter === 'bear' ? 'scale-110' : ''}`}
              >
                <circle cx="14" cy="12" r="8" fill="#FFB8B8" />
                <circle cx="34" cy="12" r="8" fill="#FFB8B8" />
                <circle cx="24" cy="26" r="16" fill="#FFCACA" />
                <circle cx="19" cy="24" r="2.5" fill="#8B4513" />
                <circle cx="29" cy="24" r="2.5" fill="#8B4513" />
                <path d="M24 28 Q24 32 24 32" stroke="#8B4513" strokeWidth="2" strokeLinecap="round" />
                <path d="M21 32 Q24 34 27 32" stroke="#FF9999" strokeWidth="2" strokeLinecap="round" fill="none" />
              </svg>
              <span className={`text-sm font-bold ${selectedCharacter === 'bear' ? 'text-pink-500' : 'text-slate-500'}`}>
                小熊 Bear
              </span>
            </button>

            {/* Rabbit Option */}
            <button
              onClick={() => setSelectedCharacter('rabbit')}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all duration-300 ${
                selectedCharacter === 'rabbit'
                  ? 'bg-pink-50 border-pink-300 shadow-lg shadow-pink-200 scale-105'
                  : 'bg-white border-slate-200 hover:border-pink-200 hover:shadow-md'
              }`}
            >
              <svg 
                width="40" 
                height="40" 
                viewBox="0 0 48 48" 
                fill="none"
                className={`transition-transform ${selectedCharacter === 'rabbit' ? 'scale-110' : ''}`}
              >
                <ellipse cx="16" cy="12" rx="5" ry="14" fill="#FFE4E4" />
                <ellipse cx="32" cy="12" rx="5" ry="14" fill="#FFE4E4" />
                <ellipse cx="16" cy="12" rx="2.5" ry="10" fill="#FFC9C9" />
                <ellipse cx="32" cy="12" rx="2.5" ry="10" fill="#FFC9C9" />
                <circle cx="24" cy="28" r="14" fill="#FFF0F0" />
                <circle cx="20" cy="26" r="2" fill="#8B4513" />
                <circle cx="28" cy="26" r="2" fill="#8B4513" />
                <circle cx="24" cy="30" r="1.5" fill="#FFB8D0" />
                <path d="M21 33 Q24 35 27 33" stroke="#FFB8D0" strokeWidth="1.5" strokeLinecap="round" fill="none" />
              </svg>
              <span className={`text-sm font-bold ${selectedCharacter === 'rabbit' ? 'text-pink-500' : 'text-slate-500'}`}>
                兔子 Rabbit
              </span>
            </button>

            {/* Cat Option */}
            <button
              onClick={() => setSelectedCharacter('cat')}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all duration-300 ${
                selectedCharacter === 'cat'
                  ? 'bg-pink-50 border-pink-300 shadow-lg shadow-pink-200 scale-105'
                  : 'bg-white border-slate-200 hover:border-pink-200 hover:shadow-md'
              }`}
            >
              <svg 
                width="40" 
                height="40" 
                viewBox="0 0 48 48" 
                fill="none"
                className={`transition-transform ${selectedCharacter === 'cat' ? 'scale-110' : ''}`}
              >
                <path d="M12 20 L8 8 L16 16 Z" fill="#FFD5B8" />
                <path d="M36 20 L40 8 L32 16 Z" fill="#FFD5B8" />
                <circle cx="24" cy="26" r="15" fill="#FFE0C8" />
                <circle cx="19" cy="24" r="2.5" fill="#8B4513" />
                <circle cx="29" cy="24" r="2.5" fill="#8B4513" />
                <circle cx="24" cy="29" r="1.5" fill="#FFB8B8" />
                <path d="M24 29 L24 32" stroke="#8B4513" strokeWidth="1.5" strokeLinecap="round" />
                <path d="M20 32 Q24 34 28 32" stroke="#FFB8B8" strokeWidth="2" strokeLinecap="round" fill="none" />
                <path d="M16 26 Q12 26 10 24" stroke="#D4A574" strokeWidth="1.5" strokeLinecap="round" />
                <path d="M32 26 Q36 26 38 24" stroke="#D4A574" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              <span className={`text-sm font-bold ${selectedCharacter === 'cat' ? 'text-pink-500' : 'text-slate-500'}`}>
                小猫 Cat
              </span>
            </button>
          </div>
        </div>

        {/* Generate Button */}
        <button 
          onClick={handleGenerate}
          disabled={isGenerating || (!vsModeData.leftScenario.title || !vsModeData.rightScenario.title)}
          className={`w-full py-4 rounded-2xl font-bold text-white text-lg shadow-lg shadow-blue-200 flex items-center justify-center transition-all transform hover:scale-[1.02] active:scale-[0.98]
            ${(!vsModeData.leftScenario.title || !vsModeData.rightScenario.title) ? 'bg-slate-300 cursor-not-allowed' : 'bg-gradient-to-r from-blue-400 to-purple-400 hover:shadow-blue-300'}
          `}
        >
          {isGenerating ? (
            <span className="animate-pulse">Generating...</span>
          ) : (
            <>
              <Sparkles className="mr-2" /> Generate VS Image
            </>
          )}
        </button>
      </div>
    </div>
  );
};

const NanoFlowUI = () => {
  // 模式状态
  const [mode, setMode] = useState<Mode>('flow');
  
  // Flow Mode 状态管理
  const [title, setTitle] = useState('');
  const [steps, setSteps] = useState<Step[]>([
    { id: 1, title: '步骤 1', desc: '' },
    { id: 2, title: '步骤 2', desc: '' }
  ]);
  
  // VS Mode 状态管理
  const [vsModeData, setVsModeData] = useState<VSModeData>({
    mainTitle: '',
    leftScenario: {
      title: '',
      description: ''
    },
    rightScenario: {
      title: '',
      description: ''
    },
    actions: ['', '', '', '']
  });
  const [actionCount, setActionCount] = useState(4);
  
  // 通用状态
  const [isGenerating, setIsGenerating] = useState(false);
  const [hasResult, setHasResult] = useState(false);
  const [loadingText, setLoadingText] = useState('正在分析需求... 🧠');
  const [progress, setProgress] = useState(0);
  
  // 分离两个模式的图片URL状态
  const [flowGeneratedImageUrl, setFlowGeneratedImageUrl] = useState<string | null>(null);
  const [vsGeneratedImageUrl, setVsGeneratedImageUrl] = useState<string | null>(null);
  
  const [error, setError] = useState<string | null>(null);
  const [selectedCharacter, setSelectedCharacter] = useState<'bear' | 'rabbit' | 'cat'>('bear');
  const [isGeneratingSteps, setIsGeneratingSteps] = useState(false);

  // 模拟"智能填充"功能 (PRD P0功能)
  const handleSmartFill = async () => {
    const hasTitle = title.trim().length > 0;

    // 场景1: 输入框为空 - 生成示例
    if (!hasTitle) {
      setTitle('如何制作美味拿铁');
      setSteps([
        { id: 1, title: '研磨咖啡豆', desc: '选择新鲜的中深烘焙豆子' },
        { id: 2, title: '萃取浓缩', desc: '使用咖啡机萃取双份Espresso' },
        { id: 3, title: '打发牛奶', desc: '将牛奶打发至绵密奶泡状态' },
        { id: 4, title: '融合拉花', desc: '将牛奶倒入咖啡并制作图案' },
      ]);
      return;
    }

    // 场景2: 输入框有内容 - 根据标题生成步骤
    try {
      setIsGeneratingSteps(true);
      setError(null);

      const response = await generateSteps(title);
      
      // 将返回的步骤转换为组件所需的格式
      const newSteps = response.steps.map((step, index) => ({
        id: index + 1,
        title: step.title,
        desc: step.description
      }));

      setSteps(newSteps);
    } catch (err) {
      console.error('Generate steps error:', err);
      setError(err instanceof Error ? err.message : '生成步骤失败，请重试');
    } finally {
      setIsGeneratingSteps(false);
    }
  };

  // 清空/重置功能
  const handleClear = () => {
    if (window.confirm('确定要清空当前内容吗？')) {
      if (mode === 'flow') {
        setTitle('');
        setSteps([
          { id: 1, title: '步骤 1', desc: '' },
          { id: 2, title: '步骤 2', desc: '' }
        ]);
      } else {
        setVsModeData({
          mainTitle: '',
          leftScenario: { title: '', description: '' },
          rightScenario: { title: '', description: '' },
          actions: ['', '', '', '']
        });
        setActionCount(4);
      }
      setHasResult(false);
      setFlowGeneratedImageUrl(null);
      setVsGeneratedImageUrl(null);
      setError(null);
    }
  };

  // 检查是否有内容
  const hasContent = () => {
    if (mode === 'flow') {
      if (title.trim()) return true;
      return steps.some(step => step.title.trim() || step.desc.trim());
    } else {
      return vsModeData.leftScenario.title.trim() || 
             vsModeData.leftScenario.description.trim() ||
             vsModeData.rightScenario.title.trim() || 
             vsModeData.rightScenario.description.trim() ||
             vsModeData.actions.some(action => action.trim());
    }
  };
  
  // 更新 VS Mode 的 actions 数量
  const updateActionCount = (count: number) => {
    setActionCount(count);
    const newActions = [...vsModeData.actions];
    if (count > newActions.length) {
      // 增加空字符串
      while (newActions.length < count) {
        newActions.push('');
      }
    } else {
      // 减少到指定数量
      newActions.length = count;
    }
    setVsModeData({ ...vsModeData, actions: newActions });
  };

  // 真实的生成过程 - 调用后端API
  const handleGenerate = async () => {
    if (mode === 'flow') {
      if (!title || steps.length < 2) {
        setError('请填写标题和至少2个步骤');
        return;
      }
    } else {
      // VS Mode: 至少需要一个场景的标题
      if (!vsModeData.leftScenario.title && !vsModeData.rightScenario.title) {
        setError('请至少填写一个场景标题');
        return;
      }
    }

    try {
      setIsGenerating(true);
      setHasResult(false);
      setError(null);
      setProgress(0);
      setLoadingText('正在分析需求... 🧠');

      // 自动生成 VS Mode 的 mainTitle
      let autoGeneratedTitle = '';
      if (mode === 'vs') {
        const leftTitle = vsModeData.leftScenario.title.trim();
        const rightTitle = vsModeData.rightScenario.title.trim();
        
        if (leftTitle && rightTitle) {
          autoGeneratedTitle = `${leftTitle} vs ${rightTitle}`;
        } else if (leftTitle) {
          autoGeneratedTitle = `${leftTitle} VS`;
        } else if (rightTitle) {
          autoGeneratedTitle = `VS ${rightTitle}`;
        } else {
          autoGeneratedTitle = 'VS';
        }
      }

      // 构建请求数据并创建生成任务
      let createResponse: GenerateResponse;
      
      if (mode === 'flow') {
        // Flow Mode: 使用原有的 /api/v1/generate 接口
        const request: GenerateRequest = {
          title: title,
          steps: steps.map(step => ({
            title: step.title,
            description: step.desc
          })),
          visual_preferences: {
            character: selectedCharacter,
            color_scheme: 'pastel',
            custom_tags: ['kawaii', 'flat']
          },
          seed: null
        };
        
        createResponse = await createGenerationTask(request);
      } else {
        // VS Mode: 使用新的 /api/v1/generate-vs 接口，使用专门的请求格式
        const vsRequest: GenerateVSRequest = {
          title: autoGeneratedTitle,
          left_scenario: {
            title: vsModeData.leftScenario.title,
            description: vsModeData.leftScenario.description
          },
          right_scenario: {
            title: vsModeData.rightScenario.title,
            description: vsModeData.rightScenario.description
          },
          actions: vsModeData.actions.slice(0, actionCount).filter(action => action.trim()),
          visual_preferences: {
            character: selectedCharacter,
            color_scheme: 'pastel',
            custom_tags: ['kawaii', 'flat']
          },
          seed: null
        };
        
        createResponse = await createVSGenerationTask(vsRequest);
      }
      
      setLoadingText(createResponse.message);

      // 轮询任务状态
      await pollTaskUntilComplete(
        createResponse.task_id,
        (task: TaskResponse) => {
          // 更新进度和消息
          setProgress(task.progress || 0);
          setLoadingText(task.message || '生成中...');

          // 如果任务完成，设置结果
          if (task.status === 'completed' && task.result) {
            // 根据当前模式设置对应的图片URL
            if (mode === 'flow') {
              setFlowGeneratedImageUrl(task.result.image_url);
            } else {
              setVsGeneratedImageUrl(task.result.image_url);
            }
            setHasResult(true);
            setIsGenerating(false);
          }
        },
        2000 // 每2秒轮询一次
      );

    } catch (err) {
      console.error('Generation error:', err);
      setError(err instanceof Error ? err.message : '生成失败，请重试');
      setIsGenerating(false);
      setHasResult(false);
    }
  };

  const addStep = () => {
    const newId = steps.length > 0 ? steps[steps.length - 1].id + 1 : 1;
    setSteps([...steps, { id: newId, title: `步骤 ${steps.length + 1}`, desc: '' }]);
  };

  const removeStep = (id: number) => {
    setSteps(steps.filter(step => step.id !== id));
  };

  return (
    <div className="min-h-screen bg-pink-50 p-4 md:p-8 font-sans text-slate-700">
      {/* Header */}
      <header className="max-w-6xl mx-auto mb-8 text-center">
        <div className="inline-flex items-center justify-center p-3 bg-white rounded-full shadow-sm mb-4">
          <span className="text-2xl mr-2">🍌</span>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-pink-400 to-blue-400 bg-clip-text text-transparent">
            Nano Flow
          </h1>
        </div>
        <p className="text-slate-500">一键生成你的可爱风格流程图 (Kawaii Infographic)</p>
        
        {/* Mode Switcher */}
        <div className="flex justify-center gap-3 mt-6">
          <button
            onClick={() => setMode('flow')}
            className={`px-6 py-3 rounded-2xl font-bold transition-all duration-300 ${
              mode === 'flow'
                ? 'bg-gradient-to-r from-pink-400 to-orange-400 text-white shadow-lg shadow-pink-200 scale-105'
                : 'bg-white text-slate-500 hover:bg-slate-50 border-2 border-slate-200'
            }`}
          >
            📊 流程图 Flow Mode
          </button>
          <button
            onClick={() => setMode('vs')}
            className={`px-6 py-3 rounded-2xl font-bold transition-all duration-300 ${
              mode === 'vs'
                ? 'bg-gradient-to-r from-blue-400 to-purple-400 text-white shadow-lg shadow-blue-200 scale-105'
                : 'bg-white text-slate-500 hover:bg-slate-50 border-2 border-slate-200'
            }`}
          >
            ⚡ 对比模式 VS Mode
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Input Zone */}
        {mode === 'flow' ? (
          <FlowModeInputPanel 
            title={title}
            setTitle={setTitle}
            steps={steps}
            setSteps={setSteps}
            selectedCharacter={selectedCharacter}
            setSelectedCharacter={setSelectedCharacter}
            isGeneratingSteps={isGeneratingSteps}
            handleSmartFill={handleSmartFill}
            handleClear={handleClear}
            hasContent={hasContent}
            addStep={addStep}
            removeStep={removeStep}
            handleGenerate={handleGenerate}
            isGenerating={isGenerating}
          />
        ) : (
          <VSModeInputPanel 
            vsModeData={vsModeData}
            setVsModeData={setVsModeData}
            actionCount={actionCount}
            updateActionCount={updateActionCount}
            handleClear={handleClear}
            hasContent={hasContent}
            handleGenerate={handleGenerate}
            isGenerating={isGenerating}
            selectedCharacter={selectedCharacter}
            setSelectedCharacter={setSelectedCharacter}
          />
        )}
        
        {/* Right Column: Preview Zone */}
        <div className="lg:col-span-7">
          {mode === 'flow' ? (
            <FlowModePreview 
              isGenerating={isGenerating}
              hasResult={hasResult}
              generatedImageUrl={flowGeneratedImageUrl}
              title={title}
              error={error}
              setError={setError}
              loadingText={loadingText}
              progress={progress}
              handleGenerate={handleGenerate}
            />
          ) : (
            <VSModePreview 
              isGenerating={isGenerating}
              hasResult={hasResult}
              generatedImageUrl={vsGeneratedImageUrl}
              vsModeData={vsModeData}
              error={error}
              setError={setError}
              loadingText={loadingText}
              progress={progress}
              handleGenerate={handleGenerate}
            />
          )}
        </div>
      </main>

      <style>{`
        .animate-bounce-slow {
          animation: bounce 3s infinite;
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default NanoFlowUI;
