/* Pure presentation of recorded states. Never interprets chart pixels as presence. */
(function(root){
 'use strict';
 const finite=v=>typeof v==='number'&&Number.isFinite(v);
 function plot(series,start,end){
   if(!finite(start)||!finite(end)||start>=end)return {segments:[],labels:[],error:'invalid_window'};
   if(series?.unit_conflict)return {segments:[],labels:[],error:'unit_conflict'};
   const numeric=series?.kind==='numeric';
   const points=(Array.isArray(series?.points)?series.points:[]).filter(p=>Array.isArray(p)&&p.length===2&&finite(p[0])&&p[0]>=start&&p[0]<=end)
     .map(([t,v])=>[t,numeric?(finite(v)?v:null):(typeof v==='string'&&v.length<=200?v:null)]).sort((a,b)=>a[0]-b[0]);
   const values=points.map(p=>p[1]).filter(v=>v!==null);
   if(!values.length)return {segments:[],labels:[],error:'no_values'};
   const categories=numeric?[]:[...new Set(values)].sort();
   if(categories.length>12)return {segments:[],labels:[],error:'too_many_categories'};
   const min=numeric?Math.min(...values):0,max=numeric?Math.max(...values):Math.max(categories.length-1,1);
   const x=t=>40+(t-start)/(end-start)*750;
   const y=v=>numeric?120-(v-min)/(max-min||1)*90:120-categories.indexOf(v)/max*90;
   const labels=numeric?[{y:20,value:max},{y:132,value:min}]:categories.map(v=>({y:y(v),value:v}));
   let current=[];const segments=[];
   for(const [t,v] of points){if(v===null){if(current.length)segments.push(current);current=[];continue;}current.push({x:x(t),y:y(v),value:v,at:t});}
   if(current.length)segments.push(current);
   return {segments,labels,numeric,error:null};
 }
 const api=Object.freeze({plot});if(typeof module!=='undefined'&&module.exports)module.exports=api;if(root)root.PilotSuiteZonePresenceModel=api;
})(typeof window!=='undefined'?window:null);
