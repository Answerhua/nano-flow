import React, { useState, useEffect } from 'react';
import { Sparkles, Plus, Trash2, Download, RefreshCw, Wand2, Image as ImageIcon } from 'lucide-react';

const NanoFlowUI = () => {
  // 模拟的状态
  const [title, setTitle] = useState('');
  const [steps, setSteps] = useState([
    { id: 1, title: '步骤 1', desc: '' },
    { id: 2, title: '步骤 2', desc: '' }
  ]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [hasResult, setHasResult] = useState(false);
  const [loadingText, setLoadingText] = useState('正在分析需求... 🧠');

  // 模拟“智能填充”功能 (PRD P0功能)
  const handleSmartFill = () => {
    setTitle('如何制作美味拿铁');
    setSteps([
      { id: 1, title: '研磨咖啡豆', desc: '选择新鲜的中深烘焙豆子' },
      { id: 2, title: '萃取浓缩', desc: '使用咖啡机萃取双份Espresso' },
      { id: 3, title: '打发牛奶', desc: '将牛奶打发至绵密奶泡状态' },
      { id: 4, title: '融合拉花', desc: '将牛奶倒入咖啡并制作图案' },
    ]);
  };

  // 模拟生成过程
  const handleGenerate = () => {
    if (!title) return;
    setIsGenerating(true);
    setHasResult(false);
    
    // 模拟 PRD 中的可爱加载文案
    const texts = [
      '正在分析需求... 🧠',
      '正在召唤画图小精灵... 🧚‍♀️',
      '正在给线条上色... 🎨',
      '最后调整光影... ✨'
    ];
    
    let i = 0;
    const interval = setInterval(() => {
      setLoadingText(texts[i % texts.length]);
      i++;
    }, 800);

    setTimeout(() => {
      clearInterval(interval);
      setIsGenerating(false);
      setHasResult(true);
    }, 3500);
  };

  const addStep = () => {
    const newId = steps.length > 0 ? steps[steps.length - 1].id + 1 : 1;
    setSteps([...steps, { id: newId, title: `步骤 ${steps.length + 1}`, desc: '' }]);
  };

  const removeStep = (id) => {
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
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Input Zone */}
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
                  placeholder="例如: Vibe Coding 开发流程"
                  className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl px-4 py-3 focus:outline-none focus:border-pink-300 transition-colors"
                />
                <button 
                  onClick={handleSmartFill}
                  className="p-3 bg-blue-50 text-blue-400 rounded-2xl hover:bg-blue-100 transition-colors tooltip"
                  title="AI 智能填充"
                >
                  <Wand2 size={20} />
                </button>
              </div>
            </div>

            {/* Steps Timeline */}
            <div className="space-y-4 mb-8">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-bold text-slate-400 uppercase tracking-wider">Flow Steps</label>
                <span className="text-xs text-pink-400 bg-pink-50 px-2 py-1 rounded-full">{steps.length} Steps</span>
              </div>
              
              <div className="relative pl-4 border-l-2 border-dashed border-slate-200 space-y-6">
                {steps.map((step, index) => (
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
                        placeholder="描述这一步在做什么..."
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

        {/* Right Column: Preview Zone */}
        <div className="lg:col-span-7">
          <div className="h-full min-h-[500px] bg-white rounded-3xl p-2 border-4 border-white shadow-xl shadow-blue-50 flex flex-col">
            <div className="flex-1 bg-slate-50 rounded-2xl flex flex-col items-center justify-center overflow-hidden relative group">
              
              {/* Empty State */}
              {!isGenerating && !hasResult && (
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
                  <p className="text-lg font-medium text-slate-600 animate-pulse">{loadingText}</p>
                </div>
              )}

              {/* Result Mockup */}
              {hasResult && (
                <div className="relative w-full h-full bg-[#FFF8E7] flex flex-col items-center justify-center p-8 animate-fade-in">
                  {/* 这里模拟生成出的 Nano Banana Pro 风格图片 */}
                  <div className="w-full max-w-md aspect-video bg-white rounded-xl shadow-sm border-2 border-slate-800 p-4 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-2 bg-pink-300"></div>
                    <div className="flex justify-center mt-2 mb-4">
                      <span className="font-bold text-slate-800 text-lg border-b-2 border-yellow-300">{title}</span>
                    </div>
                    <div className="flex justify-between items-center gap-2">
                       {/* 模拟步骤图 */}
                       {[1,2,3].map(i => (
                         <div key={i} className="flex-1 flex flex-col items-center gap-2">
                            <div className="w-12 h-12 rounded-full bg-blue-100 border-2 border-slate-800 flex items-center justify-center">
                              🐻
                            </div>
                            <div className="h-1 w-full bg-slate-200 rounded-full"></div>
                         </div>
                       ))}
                    </div>
                    <div className="absolute bottom-2 right-2 text-[10px] text-slate-400">Generatd by Nano Flow</div>
                  </div>
                </div>
              )}
            </div>

            {/* Action Bar */}
            {hasResult && (
              <div className="p-4 flex gap-3 justify-end">
                <button className="flex items-center px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-xl transition-colors text-sm font-bold">
                  <RefreshCw size={16} className="mr-2" /> Regenerate
                </button>
                <button className="flex items-center px-6 py-2 bg-slate-800 text-white hover:bg-slate-700 rounded-xl transition-colors text-sm font-bold shadow-lg shadow-slate-200">
                  <Download size={16} className="mr-2" /> Download
                </button>
              </div>
            )}
          </div>
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