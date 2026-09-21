# atguigu/query_process/nodes/node_rrf.py

from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.logger import logger
from tool.json_format_tool import json_format


class NodeRrf(NodeBase):
    """
    节点功能：Reciprocal Rank Fusion
    将多路召回的结果（向量、HyDE、Web）进行加权融合排序。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_rrf"

    def process(self, state: QueryGraphState):
        embedding_chunks = state.get("embedding_chunks")
        hyde_embedding_chunks = state.get("hyde_embedding_chunks")
        weight_embedding_chunks = [
            (embedding_chunks,1),
            (hyde_embedding_chunks,1),
        ]
        rrf_dict = {}
        for chunks,weight in weight_embedding_chunks:
            for idx,chunk in enumerate(chunks,start=1):
                chunk_id = chunk.get("id")
                score = weight / (60+idx)
                if chunk_id in rrf_dict:
                    rrf_dict[chunk_id]["score"] += score
                else:
                    chunk["score"] = score
                    rrf_dict[chunk_id] = chunk
        return {
            "rrf_chunks":sorted(rrf_dict.values(),key=lambda x:x['score'],reverse=True)[:10]
        }

if __name__ == "__main__":
    mock_state = {
        "embedding_chunks":[
            {
                "id": 469136770004048186,
                "title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8286306262016296,
                "source": "local"
            },
            {
                "id": 469136770004048187,
                "title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8241270184516907,
                "source": "local"
            },
            {
                "id": 469136770004048200,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![图片警示：禁止用手或工具触碰设备内部的齿轮/传动部件，避免手指卷入造成伤害；强调操作时需谨慎，防止人员受伤。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8219110369682312,
                "source": "local"
            },
            {
                "id": 469136770004048195,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n![图片警示：设备内部高温部件（170°C/338°F）可能导致烧伤，操作前需冷却；禁止触摸灰色标记区域；同时提示避免湿手插拔电源，防止触电。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg)  \n儎⑟ഴḽ䆜઀ᛞ࠽व䀜᪮儎⑟Ⲻ䇴༽䜞ԬȾ",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8146350383758545,
                "source": "local"
            },
            {
                "id": 469136770004048204,
                "title": "## 为设备选择一个安全的位置",
                "file_title": "hak180产品安全手册",
                "content": "## 为设备选择一个安全的位置\n\n![图片示意正确与错误的设备搬运方式：错误做法是单手提握进纸托板或出纸盒；正确做法是双手稳握设备底部两侧，避免部件脱落或设备跌落。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg)",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8131169080734253,
                "source": "local"
            },
            {
                "id": 469136770004048196,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n![图片展示了一只手正在操作打开的设备内部部件，提示用户：设备内部零件高温，勿触摸灰色标记区域；同时强调使用起搏器者需注意弱磁场影响，并遵守安全操作规范。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg)",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8093124032020569,
                "source": "local"
            },
            {
                "id": 469136770004048207,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。\n",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8067789673805237,
                "source": "local"
            },
            {
                "id": 469136770004048190,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t请先阅读这本手册，再尝试操作本设备或尝试进行任何维护。不按照这些说明操作可能会提高发生人员受伤或财产损坏（包括火灾、触电、烧伤或窒息所致）的风险。对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t请勿在未去除所有包装材料的情况下使用本设备，包括本设备内部的任何附加的包装材料。否则可能会产生火灾的风险。\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.805081307888031,
                "source": "local"
            },
            {
                "id": 469136770004048191,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.6998941898345947,
                "source": "local"
            },
            {
                "id": 469136770004048206,
                "title": "## 为设备选择一个安全的位置",
                "file_title": "hak180产品安全手册",
                "content": "## 为设备选择一个安全的位置\n\n![图示禁止将设备放置在桌边或支架边缘，尤其避免出纸盒打开时悬空；应确保设备置于平整、水平、稳定的表面，防止跌落造成人身伤害或设备损坏。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg)\n\n“重要事项”表示可能导致财产损失或本设备功能丧失的潜在危险情况。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.6912568807601929,
                "source": "local"
            }
        ],
        "hyde_embedding_chunks":[
            {
                "id": 469136770004048195,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n![图片警示：设备内部高温部件（170°C/338°F）可能导致烧伤，操作前需冷却；禁止触摸灰色标记区域；同时提示避免湿手插拔电源，防止触电。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg)  \n儎⑟ഴḽ䆜઀ᛞ࠽व䀜᪮儎⑟Ⲻ䇴༽䜞ԬȾ",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.8027992248535156,
                "source": "local"
            },
            {
                "id": 469136770004048196,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n![图片展示了一只手正在操作打开的设备内部部件，提示用户：设备内部零件高温，勿触摸灰色标记区域；同时强调使用起搏器者需注意弱磁场影响，并遵守安全操作规范。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/501bb8d2d681e4502d87badb15a68939eadfa086d309c3599f1c36b0bc559177.jpg)",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.7897841930389404,
                "source": "local"
            },
            {
                "id": 469136770004048200,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![图片警示：禁止用手或工具触碰设备内部的齿轮/传动部件，避免手指卷入造成伤害；强调操作时需谨慎，防止人员受伤。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.7895299196243286,
                "source": "local"
            },
            {
                "id": 469136770004048201,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n![图片显示一只手正将纸张放入打印机进纸托盘，左上角有禁止符号（圆圈斜线），提示“勿将手指伸入图示区域”，强调操作时需避免手部靠近设备内部危险部位，以防夹伤。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.7834056615829468,
                "source": "local"
            },
            {
                "id": 469136770004048191,
                "title": "## 设备",
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.7814344763755798,
                "source": "local"
            },
            {
                "id": 469136770004048204,
                "title": "## 为设备选择一个安全的位置",
                "file_title": "hak180产品安全手册",
                "content": "## 为设备选择一个安全的位置\n\n![图片示意正确与错误的设备搬运方式：错误做法是单手提握进纸托板或出纸盒；正确做法是双手稳握设备底部两侧，避免部件脱落或设备跌落。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg)",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.5386542677879333,
                "source": "local"
            },
            {
                "id": 469136770004048186,
                "title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.5378002524375916,
                "source": "local"
            },
            {
                "id": 469136770004048185,
                "title": "无标题",
                "file_title": "hak180产品安全手册",
                "content": "![该图片为HAK 180烫金机产品安全手册封面，包含条形码、产品型号D01WD7001-00、品牌SCHN及“产品安全手册（简体中文）”字样，提示用户使用前需阅读手册并妥善保管。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.5313929915428162,
                "source": "local"
            },
            {
                "id": 469136770004048187,
                "title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.5300501585006714,
                "source": "local"
            },
            {
                "id": 469136770004048206,
                "title": "## 为设备选择一个安全的位置",
                "file_title": "hak180产品安全手册",
                "content": "## 为设备选择一个安全的位置\n\n![图示禁止将设备放置在桌边或支架边缘，尤其避免出纸盒打开时悬空；应确保设备置于平整、水平、稳定的表面，防止跌落造成人身伤害或设备损坏。](http://192.168.100.100:9000/knowledge-base/upload-images/20260918/hak180产品安全手册/8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg)\n\n“重要事项”表示可能导致财产损失或本设备功能丧失的潜在危险情况。",
                "item_name": "HAK180烫金机（型号：D01WD7001-00，品牌：SCHN）",
                "score": 0.5272772312164307,
                "source": "local"
            }
        ]
    }

    node_rrf = NodeRrf()
    result = node_rrf(mock_state)
    logger.info(json_format(result))