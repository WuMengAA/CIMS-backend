package v1

import (
	"io"
	"net/http"

	"github.com/MINIOpenSource/CIMS-backend/internal/proto/Protobuf/Enum"
	"github.com/MINIOpenSource/CIMS-backend/internal/service"
	"github.com/gin-gonic/gin"
)

type MgmtHandler struct {
	configService   *service.ConfigService
	clientService   *service.ClientService
	commandService  *service.CommandService
}

func NewMgmtHandler() *MgmtHandler {
	return &MgmtHandler{
		configService:   service.NewConfigService(),
		clientService:   service.NewClientService(),
		commandService:  service.GetCommandService(),
	}
}

func (h *MgmtHandler) RegisterRoutes(r *gin.RouterGroup) {
	cmdGroup := r.Group("/command")
	{
		cmdGroup.GET("/datas/:resource_type/list", h.ListResources)
		cmdGroup.GET("/datas/:resource_type/create", h.CreateResource)
		cmdGroup.DELETE("/datas/:resource_type/delete", h.DeleteResource)
		cmdGroup.PUT("/datas/:resource_type/write", h.WriteResource)
		cmdGroup.POST("/datas/:resource_type/write", h.WriteResource)

		cmdGroup.GET("/clients/list", h.ListClients)
		cmdGroup.GET("/clients/status", h.ClientStatus)
		cmdGroup.GET("/client/:uid/details", h.ClientDetails)

		cmdGroup.GET("/client/:uid/restart", h.RestartClient)
		cmdGroup.GET("/client/:uid/update_data", h.UpdateClientData)
		cmdGroup.POST("/client/:uid/send_notification", h.SendNotification)
	}
}

func (h *MgmtHandler) ListResources(c *gin.Context) {
	rType := c.Param("resource_type")
	list, err := h.configService.ListFiles(rType)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": err.Error()})
		return
	}
	c.JSON(http.StatusOK, list)
}

func (h *MgmtHandler) CreateResource(c *gin.Context) {
	rType := c.Param("resource_type")
	name := c.Query("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"status": "error", "message": "name required"})
		return
	}
	// Initial content is empty JSON object
	err := h.saveFile(rType, name, "{}")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "success"})
}

func (h *MgmtHandler) DeleteResource(c *gin.Context) {
	rType := c.Param("resource_type")
	name := c.Query("name")
	if err := h.configService.DeleteFile(rType, name); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "success"})
}

func (h *MgmtHandler) WriteResource(c *gin.Context) {
	rType := c.Param("resource_type")
	name := c.Query("name")
	body, _ := io.ReadAll(c.Request.Body)
	if err := h.saveFile(rType, name, string(body)); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "success"})
}

func (h *MgmtHandler) saveFile(rType, name, content string) error {
	switch rType {
	case "ClassPlan":
		return h.configService.SaveClassPlanFile(name, content)
	case "TimeLayout":
		return h.configService.SaveTimeLayoutFile(name, content)
	case "Subjects":
		return h.configService.SaveSubjectFile(name, content)
	case "DefaultSettings":
		return h.configService.SaveSettingsFile(name, content)
	case "Policy":
		return h.configService.SavePolicyFile(name, content)
	default:
		return service.ErrNotFound
	}
}

func (h *MgmtHandler) ListClients(c *gin.Context) {
	clients, err := h.clientService.GetAllClients()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ids := make([]string, len(clients))
	for i, cl := range clients {
		ids[i] = cl.ID
	}
	c.JSON(http.StatusOK, ids)
}

func (h *MgmtHandler) ClientStatus(c *gin.Context) {
	clients, err := h.clientService.GetAllClients()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	var result []map[string]interface{}
	for _, cl := range clients {
		result = append(result, map[string]interface{}{
			"uid":           cl.ID,
			"name":          cl.Name,
			"status":        cl.Status,
			"lastHeartbeat": cl.LastHeartbeat,
			"ip":            cl.IP,
		})
	}
	c.JSON(http.StatusOK, result)
}

func (h *MgmtHandler) ClientDetails(c *gin.Context) {
	uid := c.Param("uid")
	cl, err := h.clientService.GetClient(uid)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Client not found"})
		return
	}
	profile, _ := h.configService.GetClientProfile(uid)

	result := map[string]interface{}{
		"uid":           cl.ID,
		"name":          cl.Name,
		"status":        cl.Status,
		"lastHeartbeat": cl.LastHeartbeat,
		"ip":            cl.IP,
		"profileConfig": profile,
	}
	c.JSON(http.StatusOK, result)
}

func (h *MgmtHandler) RestartClient(c *gin.Context) {
	uid := c.Param("uid")
	if h.commandService.SendCommand(uid, Enum.CommandTypes_RestartApp, []byte{}) {
		c.JSON(http.StatusOK, gin.H{"status": "success"})
	} else {
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "Client offline or error"})
	}
}

func (h *MgmtHandler) UpdateClientData(c *gin.Context) {
	uid := c.Param("uid")
	if h.commandService.SendCommand(uid, Enum.CommandTypes_DataUpdated, []byte{}) {
		c.JSON(http.StatusOK, gin.H{"status": "success"})
	} else {
		c.JSON(http.StatusInternalServerError, gin.H{"status": "error", "message": "Client offline or error"})
	}
}

func (h *MgmtHandler) SendNotification(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "success", "message": "Notification queued (Mock)"})
}
