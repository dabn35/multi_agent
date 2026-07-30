import ai_recs

ctx={'today':{'skin_conditions':['좁쌀 여드름','홍조/붉어짐']}, 'last7':{'report':'테스트 리포트','food_stats':{}}}
print('USE_LLM_RECS=', ai_recs.USE_LLM_RECS)
print('result=', ai_recs.recommend_with_llm(ctx))
